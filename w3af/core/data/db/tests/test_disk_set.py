# -*- coding: UTF-8 -*-
"""
Copyright 2012 Andres Riancho

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
import unittest
import threading

import pytest

from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.core.data.db.disk_set import DiskSet
from w4af.core.data.parsers.utils.form_params import FormParameters
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.dc.headers import Headers
from w4af.core.data.db.dbms import get_default_temp_db_instance
from w4af.core.data.dc.factory import dc_from_form_params


class TestDiskSet(unittest.TestCase):

    def setUp(self):
        create_temp_dir()

    @pytest.mark.smoke
    def test_add(self):
        ds = DiskSet()
        ds.add(1)
        ds.add(2)
        ds.add(3)
        ds.add(1)

        self.assertEqual(list(ds), [1, 2, 3])
        self.assertEqual(len(ds), 3)
        self.assertEqual(str(ds), '<DiskSet [1, 2, 3]>')

    def test_add_urlobject(self):
        ds = DiskSet()

        ds.add(URL('http://w4af.org/?id=2'))
        ds.add(URL('http://w4af.org/?id=3'))
        ds.add(URL('http://w4af.org/?id=3'))

        self.assertEqual(ds[0], URL('http://w4af.org/?id=2'))
        self.assertEqual(ds[1], URL('http://w4af.org/?id=3'))
        self.assertEqual(len(ds), 2)
        self.assertFalse(URL('http://w4af.org/?id=4') in ds)
        self.assertTrue(URL('http://w4af.org/?id=2') in ds)

    def test_add_QsRequest(self):
        ds = DiskSet()

        uri = URL('http://w4af.org/?id=2')
        hdr = Headers([('Referer', 'http://w4af.org/')])

        qsr1 = FuzzableRequest(uri, method='GET', headers=hdr)

        uri = URL('http://w4af.org/?id=3')
        qsr2 = FuzzableRequest(uri, method='GET', headers=hdr)

        uri = URL('http://w4af.org/?id=7')
        qsr3 = FuzzableRequest(uri, method='FOO', headers=hdr)

        ds.add(qsr1)
        ds.add(qsr2)
        ds.add(qsr2)
        ds.add(qsr1)

        self.assertEqual(ds[0], qsr1)
        self.assertEqual(ds[1], qsr2)
        self.assertFalse(qsr3 in ds)
        self.assertTrue(qsr2 in ds)
        self.assertEqual(len(ds), 2)

        # This forces an internal change in the URL object
        qsr2.get_url().url_string
        self.assertIn(qsr2, ds)

    def test_update(self):
        ds = DiskSet()
        ds.add(1)
        ds.update([2, 3, 1])

        self.assertEqual(list(ds), [1, 2, 3])

    def test_thread_safe(self):
        ds = DiskSet()

        def worker(range_inst):
            for i in range_inst:
                ds.add(i)

        threads = []
        _min = 0
        add_dups = False
        for _max in range(0, 1100, 100):

            th = threading.Thread(target=worker, args=(range(_min, _max),))
            threads.append(th)

            # For testing the uniqueness of DiskSets
            add_dups = not add_dups
            if add_dups:
                th = threading.Thread(
                    target=worker, args=(range(_min, _max),))
                threads.append(th)

            _min = _max

        for th in threads:
            th.start()

        for th in threads:
            th.join()

        for i in range(0, 1000):
            self.assertTrue(i in ds, i)

        ds_as_list = list(ds)
        self.assertEqual(len(ds_as_list), len(set(ds_as_list)))

        ds_as_list.sort()
        self.assertEqual(ds_as_list, list(range(1000)))
    
    def test_remove_table(self):
        disk_set = DiskSet()
        disk_set.add(1)
        disk_set.add(2)
        
        table_name = disk_set.table_name
        db = get_default_temp_db_instance()
        
        self.assertTrue(db.table_exists(table_name))

        disk_set.cleanup()
        
        self.assertFalse(db.table_exists(table_name))

    def test_store_fuzzable_request(self):
        form_params = FormParameters()
        form_params.add_field_by_attr_items([("name", "username"), ("value", "abc")])
        form_params.add_field_by_attr_items([("name", "address"), ("value", "")])
        form_params.set_action(URL('http://example.com/?id=1'))
        form_params.set_method('post')

        form = dc_from_form_params(form_params)

        fr = FuzzableRequest.from_form(form)

        ds = DiskSet()
        ds.add(fr)

        stored_fr = ds[0]

        self.assertEqual(stored_fr, fr)
        self.assertIsNot(stored_fr, fr)

    def test_store_fuzzable_request_two(self):
        ds = DiskSet()

        # Add a simple fr, without post-data
        fr = FuzzableRequest(URL('http://example.com/?id=1'))
        ds.add(fr)

        # Add a fr with post-data
        form_params = FormParameters()
        form_params.add_field_by_attr_items([("name", "username"), ("value", "abc")])
        form_params.add_field_by_attr_items([("name", "address"), ("value", "")])
        form_params.set_action(URL('http://example.com/?id=1'))
        form_params.set_method('post')

        form = dc_from_form_params(form_params)

        fr = FuzzableRequest.from_form(form)
        ds.add(fr)

        # Compare
        stored_fr = ds[1]

        self.assertEqual(stored_fr, fr)
        self.assertIsNot(stored_fr, fr)

    def test_table_name_with_prefix(self):
        _unittest = 'unittest'
        disk_set = DiskSet(_unittest)

        self.assertIn(_unittest, disk_set.table_name)
        db = get_default_temp_db_instance()

        self.assertTrue(db.table_exists(disk_set.table_name))

        disk_set.cleanup()

        self.assertFalse(db.table_exists(disk_set.table_name))