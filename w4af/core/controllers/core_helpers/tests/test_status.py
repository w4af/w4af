# -*- coding: UTF-8 -*-
"""
test_status.py

Copyright 2012 Andres Riancho

This file is part of w4af, https://w4af.net/ .

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

from unittest.mock import Mock

from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.core_helpers.status import (CoreStatus,
                                                       STOPPED, RUNNING,
                                                       PAUSED)


class TestStatus(unittest.TestCase):

    def test_simple(self):
        s = CoreStatus(Mock())
        
        self.assertEqual(s.get_status(), STOPPED)
        
        self.assertFalse(s.is_running())
        s.start()
        self.assertTrue(s.is_running())
        
        s.set_current_fuzzable_request('crawl', 'unittest_fr')
        s.set_running_plugin('crawl', 'unittest_plugin')
        
        expected = 'Crawling unittest_fr using crawl.unittest_plugin'
        self.assertEqual(s.get_status(), expected)
        
        s.pause(True)
        self.assertEqual(s.get_status(), PAUSED)
        
        s.pause(False)
        expected = 'Crawling unittest_fr using crawl.unittest_plugin'
        self.assertEqual(s.get_status(), expected)

        s.set_current_fuzzable_request('audit', 'unittest_fr_audit')
        s.set_running_plugin('audit', 'unittest_plugin_audit')

        expected = 'Crawling unittest_fr using crawl.unittest_plugin\n'\
                   'Auditing unittest_fr_audit using audit.unittest_plugin_audit'
        self.assertEqual(s.get_status(), expected)
        
        s.stop()
        self.assertEqual(s.get_status(), STOPPED)
        self.assertFalse(s.is_running())
    
    def test_queue_status_not_started(self):
        core = w4afCore()
        s = CoreStatus(core)
        
        self.assertEqual(s.get_crawl_input_speed(), 0)
        self.assertEqual(s.get_crawl_output_speed(), 0)
        self.assertEqual(s.get_crawl_qsize(), 0)
        self.assertEqual(s.get_crawl_current_fr(), None)
        
        self.assertEqual(s.get_audit_input_speed(), 0)
        self.assertEqual(s.get_audit_output_speed(), 0)
        self.assertEqual(s.get_audit_qsize(), 0)
        self.assertEqual(s.get_audit_current_fr(), None)

        core.worker_pool.terminate_join()