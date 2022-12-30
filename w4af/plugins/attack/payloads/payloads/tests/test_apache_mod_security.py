"""
test_apache_mod_security.py

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


@pytest.mark.w4af_moth
class test_apache_mod_security(ApachePayloadTestHelper):

    EXPECTED_RESULT = {'file': {'/etc/apache2/mods-available/security2.conf':
                                '<IfModule security2_module>\n\t# Default ...'},
                       'version': {'2.9.2 ': 'Yes'}}
    
    maxDiff = None
    
    @pytest.mark.ci_fails
    def test_apache_mod_security(self):
        result = exec_payload(self.shell, 'apache_mod_security', use_api=True)
        
        self.assertEqual(self.EXPECTED_RESULT['version'], result['version'])
        self.assertIn('/etc/apache2/mods-available/security2.conf', result['file'])
        
        file_content = result['file']['/etc/apache2/mods-available/security2.conf']
        self.assertIn('<IfModule security2_module>', file_content)