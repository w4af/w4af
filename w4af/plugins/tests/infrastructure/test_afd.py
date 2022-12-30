"""
test_afd.py

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
import re
import urllib.parse

from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse


BAD_SIG_URI = re.compile(r'.*(passwd|uname|passthru|xp_cmdshell|WINNT).*', re.I)


class TestFoundAFD(PluginTest):

    target_url = 'http://httpretty/'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {'infrastructure': (PluginConfig('afd'),)}
        }
    }

    MOCK_RESPONSES = [MockResponse(target_url, 'Home page'),
                      MockResponse(BAD_SIG_URI, 'Blocked by WAF'),
                      MockResponse(re.compile(target_url + r'.*'), 'Another page')]

    def test_afd_found_http(self):
        cfg = self._run_configs['cfg']
        self._scan(self.target_url, cfg['plugins'])

        infos = self.kb.get('afd', 'afd')

        self.assertEqual(len(infos), 1, infos)
        info = infos[0]

        self.assertEqual(info.get_name(), 'Active filter detected')
        values = [u.url_string.split('=')[1] for u in info['filtered']]

        self.assertIn(urllib.parse.quote_plus('../../../../etc/passwd'), set(values), values)


MOD_SECURITY_ANSWER = '''\
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access /
on this server.<br />
</p>
</body></html>
'''


class TestAFDShortResponses(PluginTest):

    target_url = 'http://httpretty/'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {'infrastructure': (PluginConfig('afd'),)}
        }
    }

    MOCK_RESPONSES = [MockResponse(target_url, 'hello world'),
                      MockResponse(BAD_SIG_URI, MOD_SECURITY_ANSWER, status=403),
                      MockResponse(re.compile(target_url + r'\?.*'), 'hello world')]

    def test_afd_found(self):
        cfg = self._run_configs['cfg']
        self._scan(self.target_url, cfg['plugins'])

        infos = self.kb.get('afd', 'afd')

        self.assertEqual(len(infos), 1, infos)
        info = infos[0]

        self.assertEqual(info.get_name(), 'Active filter detected')
        values = [urllib.parse.unquote(u.url_string.split('=')[1]) for u in info['filtered']]

        self.assertIn('../../../../etc/passwd', set(values), values)


class TestFoundHttpsAFD(TestFoundAFD):

    target_url = 'https://httpretty/'

    MOCK_RESPONSES = [MockResponse(target_url, 'Home page'),
                      MockResponse(BAD_SIG_URI, 'Blocked by WAF'),
                      MockResponse(re.compile(target_url + '.*'), 'Another page')]


class TestNotFoundAFD(PluginTest):

    target_url = 'http://httpretty/'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {'infrastructure': (PluginConfig('afd'),)}
        }
    }

    MOCK_RESPONSES = [MockResponse(re.compile('.*'), 'Static page')]

    def test_afd_not_found_http(self):
        cfg = self._run_configs['cfg']
        self._scan(self.target_url, cfg['plugins'])

        infos = self.kb.get('afd', 'afd')
        self.assertEqual(len(infos), 0, infos)
