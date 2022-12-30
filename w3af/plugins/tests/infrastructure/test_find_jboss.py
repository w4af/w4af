"""
test_find_jboss.py

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
class TestFindJBoss(PluginTest):

    target_url = get_w4af_moth_http()

    _run_configs = {
        'cfg': {
        'target': target_url,
        'plugins': {'infrastructure': (PluginConfig('find_jboss'),)}
        }
    }

    @pytest.mark.ci_fails
    def test_find_jboss(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        infos = self.kb.get('find_jboss', 'find_jboss')
        self.assertEqual(len(infos), 1, infos)

        info = infos[0]
        self.assertEqual('JMX Invoker enabled without Auth', info.get_name())