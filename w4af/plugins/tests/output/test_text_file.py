"""
test_text_file.py

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
import os
import pytest
import re

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.data.kb.tests.test_vuln import MockVuln
from w4af.core.data.parsers.doc.url import URL
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.smoke
@pytest.mark.moth
class TestTextFile(PluginTest):

    OUTPUT_FILE = 'output-unittest.txt'
    OUTPUT_HTTP_FILE = 'output-http-unittest.txt'
    
    target_url = get_moth_http('/audit/sql_injection/where_integer_qs.py')

    _run_configs = {
        'cfg': {
            'target': target_url + '?id=3',
            'plugins': {
                'audit': (PluginConfig('sqli'),),
                'output': (
                    PluginConfig(
                        'text_file',
                        ('output_file', OUTPUT_FILE, PluginConfig.STR),
                        ('http_output_file', OUTPUT_HTTP_FILE, PluginConfig.STR)),
                           
                )
            },
        }
    }

    def test_found_vulns(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        kb_vulns = self.kb.get('sqli', 'sqli')
        file_vulns = self._from_txt_get_vulns()
        self._analyze_output_file()
        
        self.assertEqual(len(kb_vulns), 1, kb_vulns)

        self.assertEqual(
            set(sorted([v.get_url() for v in kb_vulns])),
            set(sorted([v.get_url() for v in file_vulns]))
        )

        self.assertEqual(
            set(sorted([v.get_method() for v in kb_vulns])),
            set(sorted([v.get_method() for v in file_vulns]))
        )

    def _analyze_output_file(self):
        with open(self.OUTPUT_HTTP_FILE) as http_fh:
            output_file_content = http_fh.read()
        
        expected = ['Request 1', 'Response 1', '='*40]
        not_expected = ['Request None']
        
        for exp_str in expected:
            self.assertIn(exp_str, output_file_content)
            
        for not_exp_str in not_expected:
            self.assertNotIn(not_exp_str, output_file_content)

    def _from_txt_get_vulns(self):
        file_vulns = []
        vuln_regex = 'SQL injection in a .*? was found at: "(.*?)"' \
                     ', using HTTP method (.*?). The sent .*?data was: "(.*?)"'
        vuln_re = re.compile(vuln_regex)

        with (open(self.OUTPUT_FILE)) as output_fh:
            for line in output_fh:
                mo = vuln_re.search(line)

                if mo:
                    v = MockVuln('TestCase', None, 'High', 1, 'plugin')
                    v.set_url(URL(mo.group(1)))
                    v.set_method(mo.group(2))

                    file_vulns.append(v)

        return file_vulns

    def tearDown(self):
        for f in (self.OUTPUT_FILE, self.OUTPUT_HTTP_FILE):
            try:
                os.remove(f)
            except:
                pass