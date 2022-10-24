"""
test_ldapi.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import pytest

from w3af.core.controllers.ci.moth import get_moth_http
from w3af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.moth
class TestLDAPI(PluginTest):

    target_url = get_moth_http('/audit/LDAP/simple_ldap.php')

    _run_configs = {
        'cfg': {
            'target': target_url + '?i=xxx',
            'plugins': {
                'audit': (PluginConfig('ldapi'),),
            }
        }
    }

    @pytest.mark.ci_fails
    def test_found_ldapi(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])
        vulns = self.kb.get('ldapi', 'ldapi')
        self.assertEqual(1, len(vulns))
        # Now some tests around specific details of the found vuln
        vuln = vulns[0]
        self.assertEqual("LDAP injection vulnerability", vuln.get_name())
        self.assertEqual(self.target_url, str(vuln.get_url()))