# coding: utf8
"""
test_wordpress_fullpathdisclosure.py

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


@pytest.mark.wordpress
class TestWordpressPathDisclosure(PluginTest):

    wordpress_url = 'http://wordpress/'

    _run_configs = {
        'direct': {
            'target': wordpress_url,
            'plugins': {
        'crawl': (PluginConfig('wordpress_fullpathdisclosure',),)
            },
        },
    }

    @pytest.mark.ci_fails
    def test_enumerate_users(self):
        cfg = self._run_configs['direct']
        self._scan(cfg['target'], cfg['plugins'])

        infos = self.kb.get('wordpress_fullpathdisclosure', 'info')

        self.assertEqual(len(infos), 1, infos)
        info = infos[0]

        self.assertEqual(info.get_name(), 'WordPress path disclosure')
        self.assertEqual(info.get_url().url_string,
                         self.wordpress_url + 'wp-content/plugins/akismet/akismet.php')