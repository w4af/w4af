"""
test_directory_indexing.py

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

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.plugins.tests.helper import PluginTest, PluginConfig

import w4af.core.data.constants.severity as severity


@pytest.mark.ci_ready
@pytest.mark.moth
class TestDirectoryIndexing(PluginTest):

    dir_indexing_url = get_moth_http('/grep/directory_indexing/index.html')

    _run_configs = {
        'cfg1': {
            'target': dir_indexing_url,
            'plugins': {
                'grep': (PluginConfig('directory_indexing'),)
            }
        }
    }

    def test_found_vuln(self):
        cfg = self._run_configs['cfg1']
        self._scan(cfg['target'], cfg['plugins'])
        
        vulns = self.kb.get('directory_indexing', 'directory')
        self.assertEqual(1, len(vulns))
        v = vulns[0]
        
        self.assertEqual(self.dir_indexing_url, str(v.get_url()))
        self.assertEqual(severity.LOW, v.get_severity())
        self.assertEqual('Directory indexing',v.get_name())
