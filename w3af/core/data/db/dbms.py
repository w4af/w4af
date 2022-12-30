"""
dbms.py

Copyright 2013 Andres Riancho

This file is part of w4af, http://w4af.org/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""


import os
import sys
import sqlite3

from functools import wraps

from concurrent.futures import ThreadPoolExecutor

import w4af.core.controllers.output_manager as om

from w4af.core.data.misc.file_utils import replace_file_special_chars
from w4af.core.controllers.misc.temp_dir import get_temp_dir, create_temp_dir
from w4af.core.controllers.exceptions import (DBException,
                                              NoSuchTableException,
                                              MalformedDBException)


# Constants
SETUP = 'SETUP'
QUERY = 'QUERY'
SELECT = 'SELECT'
COMMIT = 'COMMIT'
CLOSE = 'CLOSE'

DB_MALFORMED_ERROR = ('SQLite raised a database disk image is malformed'
                      ' exception. While we do have good understanding on the'
                      ' many reasons that'
                      ' might lead to this issue [0] and multiple bug reports'
                      ' by users [1] there is no clear indication on exactly'
                      ' what causes the issue in w4af.\n\n'
                      ''
                      'If you are able to reproduce this issue in your'
                      ' environment we would love to hear the OS and hardware'
                      ' details, steps to reproduce, and any other related'
                      ' information. Just send us a comment at #4905 [1].\n\n'
                      ''
                      '[0] https://www.sqlite.org/howtocorrupt.html\n'
                      '[1] https://github.com/andresriancho/w4af/issues/4905')


def verify_started(meth):
    
    @wraps(meth)
    def inner_verify_started(self, *args, **kwds):
        msg = 'No calls to SQLiteDBMS can be made after stop().'

        assert not self.sql_executor.get_received_poison_pill(), msg

        return meth(self, *args, **kwds)
    
    return inner_verify_started


class SQLiteDBMS(object):
    """
    Wrap sqlite connection in a way that allows concurrent requests from
    multiple threads.

    This is done by internally queuing the requests and processing them
    sequentially in a separate thread (in the same order they arrived).

    For all requests performed by the client, a Future [0] is returned, in
    other words, this is an asynchronous class.
    
    [0] http://www.python.org/dev/peps/pep-3148/
    """
    def __init__(self, filename, autocommit=False, journal_mode='OFF',
                 cache_size=2000):

        super(SQLiteDBMS, self).__init__()

        #   All DB queries from w4af are sent to this queue, and this is a lot
        #   since the DiskList, DiskQueue, DiskDict classes which are used
        #   extensively through the framework use the same SQLite db as a
        #   backend (of course different tables, but the same SQLite file and
        #   on-memory instance).
        
        #    Performs sqlite database setup, this has the nice side-effect
        #    that .result() will block until the thread is started and
        #    processing tasks.
        self.sql_executor = SQLiteExecutor()
        future = self.sql_executor.setup(filename, autocommit, journal_mode,
                                          cache_size)
        # Raises an exception if an error was found during setup
        future.result()
        
        self.filename = filename
        self.autocommit = autocommit

    @verify_started
    def execute(self, query, parameters=(), commit=False):
        """
        `execute` calls are non-blocking: just queue up the request and
        return a future.
        """
        fr = self.sql_executor.query(query, parameters)
        
        if self.autocommit or commit:
            self.commit()
            
        return fr

    @verify_started
    def select(self, query, parameters=()):
        """
        I can't think about any non-blocking use of calling select()
        """
        future = self.sql_executor.select(query, parameters)
        return future.result()

    @verify_started
    def select_one(self, query, parameters=()):
        """
        :return: Only the first row of the SELECT, or None if there are no
        matching rows.
        """
        try:
            return self.select(query, parameters)[0]
        except IndexError:
            return None

    @verify_started
    def commit(self):
        # Send the task and wait for the execution
        future = self.sql_executor.commit()
        future.result()

    @verify_started
    def close(self):
        # Commit all pending changes
        self.commit()

        future = self.sql_executor.close()
        future.result()

        # Setting the received poison pill to True will make all calls to
        # SQLiteDBMS methods fail because of `@verify_started`. The goal is
        # to prevent other tasks being queued after the poison pill
        self.sql_executor.shutdown()

    def get_file_name(self):
        """Return DB filename."""
        return self.filename
    
    def drop_table(self, name):
        query = 'DROP TABLE %s' % name
        return self.execute(query, commit=True)
    
    def clear_table(self, name):
        """
        Remove all rows from a table.
        """
        query = 'DELETE FROM %s WHERE 1=1' % name
        return self.execute(query, commit=True)
    
    def create_table(self, name, columns, pk_columns=(), constraints=()):
        """
        Create table in convenient way.
        """
        if not name:
            raise ValueError('create_table requires a table name')
        
        if not columns:
            raise ValueError('create_table requires column names and types')

        if not isinstance(columns, list):
            raise ValueError('create_table requires column names and types in a list')

        if not isinstance(constraints, tuple):
            raise ValueError('constraints requires constraints in a tuple')

        # Create the table
        query = 'CREATE TABLE %s (' % name
        
        all_columns = []
        for column_data in columns:
            column_name, column_type = column_data
            all_columns.append('%s %s' % (column_name, column_type))
            
        query += ', '.join(all_columns)
        
        # Finally the PK and constraints
        if pk_columns:
            query += ', PRIMARY KEY (%s)' % ','.join(pk_columns)

        if constraints:
            for c in constraints:
                query += ', CONSTRAINT %s' % c

        query += ')'

        return self.execute(query, commit=True)

    def table_exists(self, name):
        query = ("SELECT name FROM sqlite_master WHERE type='table'"
                 " AND name=? LIMIT 1")
        r = self.select(query, (name,))
        return bool(r)        

    def create_index(self, table, columns):
        """
        Create index for speed and performance

        :param table: The table from which you want to create an index from
        :param columns: A list of column names.
        """
        query = 'CREATE INDEX %s_index ON %s( %s )' % (table, table,
                                                       ','.join(columns))

        return self.execute(query, commit=True)


class SQLiteExecutor():
    """
    A very simple thread that takes work via submit() and processes it in a
    different thread.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1,
            thread_name_prefix="SQLiteExecutor")
        self._poison_pill_received = False

    def get_received_poison_pill(self):
        return self._poison_pill_received

    def query(self, query, parameters):
        return self._submit((QUERY, (query, parameters), {}))
    
    def _query_handler(self, query, parameters):
        cursor = self.conn.cursor()
        return cursor.execute(query, parameters)

    def select(self, query, parameters):
        return self._submit((SELECT, (query, parameters), {}))
    
    def _select_handler(self, query, parameters):
        result = self.cursor.execute(query, parameters)
        result_lst = []
        for row in result:
            result_lst.append(row)
        return result_lst
    
    def commit(self):
        return self._submit((COMMIT, None, None))

    def _commit_handler(self):
        return self.conn.commit()
        
    def setup(self, filename, autocommit=False, journal_mode='OFF',
              cache_size=2000):
        """
        Request the process to perform a setup.
        """
        request = (SETUP,
                   (filename,),
                   {'autocommit': autocommit,
                    'journal_mode': journal_mode,
                    'cache_size': autocommit})
        return self._submit(request)

    def close(self):
        return self._submit((CLOSE, None, None))
    
    def _setup_handler(self, filename, autocommit=False, journal_mode='OFF',
                       cache_size=2000):
        # Convert the filename to UTF-8, this is needed for windows, and special
        # characters, see:
        # http://www.sqlite.org/c3ref/open.html
        self.filename = replace_file_special_chars(filename)

        self.autocommit = autocommit
        self.journal_mode = journal_mode
        self.cache_size = cache_size
        
        #
        #    Setup phase
        #
        if self.autocommit:
            conn = sqlite3.connect(self.filename,
                                   isolation_level=None,
                                   check_same_thread=True)
        else:
            conn = sqlite3.connect(self.filename,
                                   check_same_thread=True)
        
        conn.execute('PRAGMA journal_mode = %s' % self.journal_mode)
        conn.execute('PRAGMA cache_size = %s' % self.cache_size)
        conn.text_factory = str
        self.conn = conn
        
        self.cursor = conn.cursor()

        # Commented line to be: Slower but (hopefully) without malformed
        # databases
        #
        # https://github.com/andresriancho/w4af/issues/4937
        #
        # It doesn't seem to help because I'm still getting malformed database
        # files, but I'll keep it anyways because I'm assuming that it's going
        # to reduce (not to zero, but reduce) these issues.
        #
        #self.cursor.execute('PRAGMA synchronous=OFF')

    def _submit(self, task):
        return self.executor.submit(self._handle_task, task)

    def _close_handler(self):
        self.conn.close()
        self.conn = None

    def shutdown(self):
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.executor = None
        self._poison_pill_received = True

    def _handle_task(self, task):
        op_code, args, kwds = task

        OP_CODES = {SETUP: self._setup_handler,
                    QUERY: self._query_handler,
                    SELECT: self._select_handler,
                    COMMIT: self._commit_handler,
                    CLOSE: self._close_handler}

        handler = OP_CODES.get(op_code, None)

        if handler is None:
            # Invalid OPCODE
            return False

        try:
            if kwds is not None:
                result = handler(*args, **kwds)
            elif args is not None:
                result = handler(*args)
            else:
                result = handler()
        except sqlite3.OperationalError as e:
            # I don't like this string match, but it seems that the
            # exception doesn't have any error code to match
            if 'no such table' in str(e):
                dbe = NoSuchTableException(str(e))

            elif 'malformed' in str(e):
                print(DB_MALFORMED_ERROR)
                dbe = MalformedDBException(DB_MALFORMED_ERROR)

            else:
                # More specific exceptions to be added here later...
                dbe = DBException(str(e))

            raise dbe

        except Exception as e:
            dbe = DBException(str(e))
            raise dbe

        else:
            return result


temp_default_db = None

def get_default_temp_db_instance():
    global temp_default_db
    
    if temp_default_db is None:
        create_temp_dir()
        temp_default_db = SQLiteDBMS('%s/main.db' % get_temp_dir())
        
    return temp_default_db

def reset_temp_db_instance():
    global temp_default_db

    if temp_default_db is not None:
        temp_default_db.close()
        temp_default_db = None


def get_default_persistent_db_instance():
    """
    At some point I'll want to have persistent DB for storing the KB and other
    information across different w4af processes, or simply to save the findings
    in a KB and don't remove them. I'm adding this method as a reminder of
    where it should be done.
    """
    return get_default_temp_db_instance()
