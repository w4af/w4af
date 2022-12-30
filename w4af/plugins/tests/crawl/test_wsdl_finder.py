"""
test_wsdl_finder.py

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
class TestWSDLFinder(PluginTest):

    base_url = get_w4af_moth_http('/w4af/crawl/wsdl_finder/')

    _run_configs = {
        'cfg': {
            'target': base_url,
            'plugins': {'crawl': (PluginConfig('wsdl_finder'),
                                  PluginConfig('web_spider',
                                               (
                                               'only_forward', True, PluginConfig.BOOL))),
                        }
        }
    }

    @pytest.mark.ci_fails
    def test_wsdl_found(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        infos = self.kb.get('wsdl_greper', 'wsdl')

        self.assertEqual(len(infos), 1, infos)

        info = infos[0]

        self.assertIn('WSDL resource', info.get_name())
        self.assertEqual(info.get_url().url_string,
                          self.base_url + 'web_service_server.php')