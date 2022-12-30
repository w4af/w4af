"""
test_detect_reverse_proxy.py

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
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.w4af_moth
class TestDetectReverseProxy(PluginTest):

    proxied_url = get_w4af_moth_http('/w4af/infrastructure/detect_reverse_proxy/')
    simple_url = get_w4af_moth_http('/w4af/')

    _run_configs = {
        'cfg': {
        'target': None,
        'plugins': {'infrastructure': (PluginConfig('detect_reverse_proxy'),)}
        }
    }

    @pytest.mark.ci_fails
    def test_detect_reverse_proxy(self):
        cfg = self._run_configs['cfg']
        self._scan(self.proxied_url, cfg['plugins'])

        infos = self.kb.get('detect_reverse_proxy', 'detect_reverse_proxy')
        self.assertEqual(len(infos), 1, infos)

        info = infos[0]
        self.assertEqual('Reverse proxy identified', info.get_name())

    @pytest.mark.ci_fails
    def test_not_detect_reverse_proxy(self):
        cfg = self._run_configs['cfg']
        self._scan(self.simple_url, cfg['plugins'])

        infos = self.kb.get('detect_reverse_proxy', 'detect_reverse_proxy')
        self.assertEqual(len(infos), 0, infos)