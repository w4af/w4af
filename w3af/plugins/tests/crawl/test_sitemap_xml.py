"""
test_sitemap_reader.py

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
class TestSitemap(PluginTest):

    target_url = get_w4af_moth_http()

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {'crawl': (PluginConfig('sitemap_xml'),)}
        }
    }

    @pytest.mark.ci_fails
    def test_sitemap(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        urls = self.kb.get_all_known_urls()

        self.assertEqual(len(urls), 3, [u for u in urls])

        hidden_url = get_w4af_moth_http('/hidden/')

        for url in urls:
            if url.url_string == hidden_url:
                self.assertTrue(True)
                break
        else:
            self.assertTrue(False)