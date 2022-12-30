"""
test_urlfuzzer.py

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
from w4af.plugins.tests.helper import PluginTest, PluginConfig
from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http


@pytest.mark.w4af_moth
class TestURLFuzzer(PluginTest):

    base_url = get_w4af_moth_http('/w4af/crawl/url_fuzzer')

    _run_configs = {
        'standalone': {
            'target': base_url + '/index.html',
            'plugins': {'crawl': (PluginConfig('url_fuzzer'),)}
        },
    }

    @pytest.mark.ci_fails
    def test_fuzzer_found_urls(self):
        cfg = self._run_configs['standalone']
        self._scan(cfg['target'], cfg['plugins'])
        
        expected_urls = ('/index.html', '/index.html~',
                         '/index.html.zip', '.tgz')
        urls = self.kb.get_all_known_urls()
        
        self.assertEqual(
            set(str(u) for u in urls),
            set((self.base_url + end) for end in expected_urls)
        )
        