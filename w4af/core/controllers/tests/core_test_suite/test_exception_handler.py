"""
test_exception_handling.py

Copyright 2011 Andres Riancho

This file is part of w4af, http://w4af.net/ .

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
from w4af.core.controllers.tests.core_test_suite.test_pause_stop import CountTestMixin


class TestExceptionHandler(CountTestMixin):
    """
    Inherit from Testw4afCorePause to get the nice setUp().
    """
    def test_same_id(self):
        """
        Verify that the exception handler is the same before and after the scan
        """
        before_id_ehandler = id(self.w4afcore.exception_handler)
        
        self.w4afcore.start()
        
        after_id_ehandler = id(self.w4afcore.exception_handler)
        
        self.assertEqual(before_id_ehandler, after_id_ehandler)