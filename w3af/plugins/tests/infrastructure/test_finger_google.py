"""
test_finger_google.py

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


@pytest.mark.skip("Google searches are not working")
class TestFingerGoogle(PluginTest):

    base_url = 'http://www.w4af.org/'

    _run_configs = {
        'cfg': {
            'target': base_url,
            'plugins': {'infrastructure': (PluginConfig('finger_google'),)}
        }
    }

    @pytest.mark.ci_fails
    def test_fuzzer_user(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        emails = self.kb.get('emails', 'emails')

        self.assertEqual(len(emails), 3, emails)
        
        users = [em['user'] for em in emails]
        self.assertNotIn('x3d', users) 