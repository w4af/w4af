"""
test_apache_htaccess.py

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
import pytest
from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload


class test_apache_htaccess(ApachePayloadTestHelper):

    EXPECTED_RESULT = {'htaccess_files':
                       {'/var/www/html/.htaccess': '#Completely useless, just to be found by the apache_htaccess payload.\n'}
                      }

    @pytest.mark.ci_fails
    @pytest.mark.w4af_moth
    def test_apache_htaccess(self):
        result = exec_payload(self.shell, 'apache_htaccess', use_api=True)
        self.assertEqual(self.EXPECTED_RESULT, result)