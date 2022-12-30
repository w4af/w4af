"""
test_base_consumer.py

Copyright 2011 Andres Riancho

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
import threading
import unittest

from unittest.mock import Mock

from w4af.core.controllers.core_helpers.consumers.base_consumer import BaseConsumer
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL


EXPECTED_THREAD_NAMES = {
    'PoolTaskHandler',
    'PoolResultHandler',
    'OutputManagerWorkerThread',
    'PoolWorkerHandler',
    'MainThread',
    'SQLiteExecutor_0',
    'OutputManager',
    'QueueFeederThread'
}

class TestBaseConsumer(unittest.TestCase):

    def setUp(self):
        self.core = w4afCore()
        self.assertEqual(self._get_running_threads(), set(EXPECTED_THREAD_NAMES))
        self.bc = BaseConsumer([], self.core, 'TestConsumer')

    def test_handle_exception(self):
        url = URL('http://moth/')
        fr = FuzzableRequest(url)
        exception = None
        try:
            raise Exception()
        except Exception as e:
            exception = e
            self.bc.handle_exception('audit', 'sqli', fr, e, store_tb=True)

        exception_data = self.bc.out_queue.get()

        self.assertTrue(exception_data.traceback is not None)
        self.assertEqual(exception_data.phase, 'audit')
        self.assertEqual(exception_data.plugin, 'sqli')
        self.assertEqual(exception_data.exception, exception)
        self.bc.terminate()
        self.assertEqual(self._get_running_threads(), set(EXPECTED_THREAD_NAMES))

    def _get_running_threads(self):
        threads = [t for t in threading.enumerate()]
        thread_names = [t.name for t in threads]

        return set(thread_names)
    
    def test_terminate(self):
        self.bc.start()
        
        self.bc._teardown = Mock()
        
        self.bc.terminate()
        
        self.assertEqual(self.bc._teardown.call_count, 1)

    def test_terminate_terminate(self):
        self.bc.start()

        self.bc._teardown = Mock()

        self.bc.terminate()

        self.assertEqual(self.bc._teardown.call_count, 1)
