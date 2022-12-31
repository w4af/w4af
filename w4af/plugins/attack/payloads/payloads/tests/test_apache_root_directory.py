"""
test_apache_root_directory.py

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
import pytest

from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload


@pytest.mark.w4af_moth
class test_apache_root_directory(ApachePayloadTestHelper):

    @pytest.mark.ci_fails
    def test_apache_root_directory(self):
        result = exec_payload(
            self.shell, 'apache_root_directory', use_api=True)
        self.assertIn('apache_root_directory', result)
        self.assertSetEqual(set(result['apache_root_directory']), set(['/var/www/html/', '/var/www/']))