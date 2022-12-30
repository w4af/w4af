"""
test_dav.py

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

from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.w4af_moth
class TestDav(PluginTest):

    target_vuln_all = get_w4af_moth_http('/w4af/audit/dav/write-all/')
    target_no_privs = get_w4af_moth_http('/w4af/audit/dav/no-privileges/')
    target_safe_all = get_w4af_moth_http('/w4af/audit/eval/')

    _run_configs = {
        'cfg': {
            'target': None,
            'plugins': {
                'audit': (PluginConfig('dav',),),
            }
        },
    }

    @pytest.mark.ci_fails
    def test_found_all_dav(self):
        cfg = self._run_configs['cfg']
        self._scan(self.target_vuln_all, cfg['plugins'])

        vulns = self.kb.get('dav', 'dav')

        EXPECTED_NAMES = set(['Insecure DAV configuration', 'Publicly writable directory'])

        self.assertEqual(EXPECTED_NAMES,
                          set([v.get_name() for v in vulns])
                          )

        self.assertEqual(set(['PUT', 'PROPFIND']),
                          set([v.get_method() for v in vulns]))

        self.assertTrue(all([self.target_vuln_all == str(
            v.get_url().get_domain_path()) for v in vulns]))

    @pytest.mark.ci_fails
    def test_no_privileges(self):
        """
        DAV is configured but the directory doesn't have the file-system permissions
        to allow the Apache process to write to it.
        """
        cfg = self._run_configs['cfg']
        self._scan(self.target_no_privs, cfg['plugins'])

        vulns = self.kb.get('dav', 'dav')

        self.assertEqual(len(vulns), 2, vulns)

        iname = 'DAV incorrect configuration'
        info_no_privs = [i for i in vulns if i.get_name() == iname][0]

        vname = 'Insecure DAV configuration'
        vuln_propfind = [v for v in vulns if v.get_name() == vname][0]
         
        info_url =  str(info_no_privs.get_url().get_domain_path())
        vuln_url =  str(vuln_propfind.get_url().get_domain_path())
        
        self.assertEqual(self.target_no_privs, info_url)
        self.assertEqual(self.target_no_privs, vuln_url)

    @pytest.mark.ci_fails
    def test_not_found_dav(self):
        cfg = self._run_configs['cfg']
        self._scan(self.target_safe_all, cfg['plugins'])

        vulns = self.kb.get('dav', 'dav')
        self.assertEqual(0, len(vulns))