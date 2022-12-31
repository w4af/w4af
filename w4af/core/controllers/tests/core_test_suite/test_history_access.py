"""
test_history_access.py

Copyright 2011 Andres Riancho

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
import pytest

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.controllers.tests.core_test_suite.test_pause_stop import CountTestMixin
from w4af.core.data.db.history import HistoryItem


@pytest.mark.moth
class TestHistoryAccess(CountTestMixin):
    """
    Test that we're able to access the HTTP request and response History after
    the scan has finished.
    
    @see: Inherit from Testw4afCorePause to get the nice setUp().
    """
    def test_history_access(self):
        self.count_plugin.loops = 1
        self.w4afcore.start()
        
        history_item = HistoryItem() 
        self.assertTrue(history_item.load(1))
        self.assertEqual(history_item.id, 1)
        self.assertEqual(history_item.get_request().get_uri().url_string,
                         get_moth_http())
        self.assertEqual(history_item.get_response().get_uri().url_string,
                         get_moth_http())
