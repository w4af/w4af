"""
test_server_header.py

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


@pytest.mark.moth
class TestServerHeader(PluginTest):

    base_url = get_moth_http()

    _run_configs = {
        'cfg': {
        'target': base_url,
        'plugins': {'infrastructure': (PluginConfig('server_header'),)}
        }
    }

    def test_find_server_power(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        server = self.kb.get('server_header', 'server')
        pow_by = self.kb.get('server_header', 'powered_by')
        pow_by_str = self.kb.raw_read('server_header', 'powered_by_string')

        self.assertEqual(len(server), 1, server)
        self.assertEqual(len(pow_by), 1, pow_by)

        self.assertEqual(server[0].get_name(), 'Server header')
        self.assertEqual(pow_by[0].get_name(), 'Powered-by header')

        self.assertIsInstance(pow_by_str, str)
        self.assertIn('PHP', pow_by_str)
        self.assertIn('ubuntu', pow_by_str)
        