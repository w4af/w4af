"""
test_json_file.py

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
import json
import os
import pytest

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.kb.tests.test_vuln import MockVuln
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.smoke
@pytest.mark.moth
class TestJsonOutput(PluginTest):

    target_url = get_moth_http('/audit/sql_injection/where_integer_qs.py')

    FILENAME = 'output-unittest.json'

    _run_configs = {
        'cfg': {
            'target': target_url + '?id=3',
            'plugins': {
                'audit': (PluginConfig('sqli'),),
                'output': (
                    PluginConfig(
                        'json_file',
                        ('output_file', FILENAME, PluginConfig.STR)),
                )
            },
        }
    }

    def test_found_vuln(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        kb_vulns = self.kb.get('sqli', 'sqli')
        file_vulns = self._from_json_get_vulns(self.FILENAME)

        self.assertEqual(len(kb_vulns), 1, kb_vulns)

        self.assertEqual(
            set(sorted([v.get_url() for v in kb_vulns])),
            set(sorted([v.get_url() for v in file_vulns])),
            set(sorted([v.get_url() for v in kb_vulns])),
        )

        self.assertEqual(
            set(sorted([v.get_name() for v in kb_vulns])),
            set(sorted([v.get_name() for v in file_vulns])),
            set(sorted([v.get_name() for v in kb_vulns]))
        )

        self.assertEqual(
            set(sorted([v.get_plugin_name() for v in kb_vulns])),
            set(sorted([v.get_plugin_name() for v in file_vulns])),
            set(sorted([v.get_plugin_name() for v in kb_vulns]))
        )

    def _from_json_get_vulns(self, filename):
        json_data = json.load(open(filename, 'r'))
        vulns = []

        for finding in json_data['items']:

            v = MockVuln(finding['Name'], None, 'High', 1, 'sqli')
            v.set_url(URL(finding['URL']))
            vulns.append(v)

        return vulns

    def tearDown(self):
        super(TestJsonOutput, self).tearDown()
        try:
            os.remove(self.FILENAME)
        except:
            pass
        finally:
            self.kb.cleanup()
