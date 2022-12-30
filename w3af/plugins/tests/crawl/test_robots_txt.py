"""
test_robots_reader.py

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
from w4af.core.data.parsers.doc.url import URL
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.w4af_moth
class TestRobots(PluginTest):

    target_url = get_w4af_moth_http('/')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {'crawl': (PluginConfig('robots_txt'),)}
        }
    }

    def test_robots(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        urls = self.kb.get_all_known_urls()
        urls = {u for u in urls}

        expected_urls = {URL(get_w4af_moth_http('/')),
                         URL(get_w4af_moth_http('/hidden/')),
                         URL(get_w4af_moth_http('/robots.txt'))}

        self.assertEqual(urls, expected_urls)
