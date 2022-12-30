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

from w4af.plugins.tests.helper import PluginConfig, ExecExploitTest
from w4af.core.data.kb.vuln_templates.dav_template import DAVTemplate
from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http


@pytest.mark.smoke
@pytest.mark.w4af_moth
class TestDAVShell(ExecExploitTest):

    target_url = get_w4af_moth_http('/w4af/audit/dav/write-all/')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('dav',),),
            }
        },
    }

    @pytest.mark.ci_fails
    def test_found_exploit_dav(self):
        # Run the scan
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        # Assert the general results
        vulns = self.kb.get('dav', 'dav')
        self.assertEqual(len(vulns), 2, vulns)

        vulns.sort(key=lambda x:x.get_name())
        vuln = vulns[0]
        self.assertEqual('Insecure DAV configuration', vuln.get_name())

        vuln_to_exploit_id = vuln.get_id()
        self._exploit_vuln(vuln_to_exploit_id, 'dav')
    
    @pytest.mark.ci_fails
    def test_from_template(self):
        dt = DAVTemplate()
        
        options = dt.get_options()
        options['url'].set_value(self.target_url)
        dt.set_options(options)

        dt.store_in_kb()
        vuln = self.kb.get(*dt.get_kb_location())[0]
        vuln_to_exploit_id = vuln.get_id()
        
        self._exploit_vuln(vuln_to_exploit_id, 'dav')
