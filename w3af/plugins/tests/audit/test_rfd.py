"""
test_rfd.py

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
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse

RUN_CONFIG = {
    'cfg': {
        'target': None,
        'plugins': {
            'audit': (PluginConfig('rfd'),),
            'crawl': (
                PluginConfig(
                    'web_spider',
                    ('only_forward', True, PluginConfig.BOOL)),
            )
        }
    }
}


class TestJSONAllFiltered(PluginTest):

    target_url = 'http://json-all-filtered/?q=rfd'

    MOCK_RESPONSES = [
              MockResponse(url='http://json-all-filtered/?q=rfd',
                           body=b'empty body',
                           content_type='application/json',
                           method='GET', status=200),
              MockResponse(url='http://json-all-filtered/%3B/w4af.cmd%3B/'
                               'w4af.cmd?q=rfd',
                           body='message "w4afExecToken"',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json-all-filtered/%3B/w4af.cmd%3B/'
                               'w4af.cmd?q=w4afExecToken',
                           body='    {"a":"w4afExecToken","b":"b"}',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json-all-filtered/%3B/w4af.cmd%3B/'
                               'w4af.cmd?q=w4afExecToken%22%26%7C%0A',
                           body='    {"a":"w4afExecToken","b":"b"}',
                           content_type='application/javascript',
                           method='GET', status=200),
              ]

    def test_not_found_json_all_filtered(self):
        cfg = RUN_CONFIG['cfg']
        self._scan(self.target_url, cfg['plugins'])
        vulns = self.kb.get('rfd', 'rfd')
        self.assertEqual(0, len(vulns))


class TestJSON(PluginTest):

    target_url = 'http://json/?q=rfd'

    MOCK_RESPONSES = [
              MockResponse(url='http://json/?q=rfd',
                           body=b'empty body',
                           content_type='application/json',
                           method='GET', status=200),
              MockResponse(url='http://json/%3B/w4af.cmd%3B/w4af.cmd?q=rfd',
                           body=b'message "w4afExecToken"',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json/%3B/w4af.cmd%3B/w4af.cmd?'
                               'q=w4afExecToken',
                           body=b'    {"a":"w4afExecToken","b":"b"}',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json/%3B/w4af.cmd%3B/w4af.cmd?'
                               'q=w4afExecToken%22%26%7C%0A',
                           body=b'    {"a":"w4afExecToken"&|\n","b":"b"}',
                           content_type='application/javascript',
                           method='GET', status=200),
              ]

    def test_found_json(self):
        cfg = RUN_CONFIG['cfg']
        self._scan(self.target_url, cfg['plugins'])
        vulns = self.kb.get('rfd', 'rfd')
        self.assertEqual(1, len(vulns))


class TestJSONDobleQuotesFiltered(PluginTest):

    target_url = 'http://json-filtered/?q=rfd'

    MOCK_RESPONSES = [
              MockResponse(url='http://json-filtered/?q=rfd',
                           body=b'empty body',
                           content_type='application/json',
                           method='GET', status=200),
              MockResponse(url='http://json-filtered/%3B/w4af.cmd%3B/w4af.cmd?q=rfd',
                           body='message "w4afExecToken"',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json-filtered/%3B/w4af.cmd%3B/w4af.cmd?'
                               'q=w4afExecToken',
                           body='    {"a":"w4afExecToken","b":"b"}',
                           content_type='text/json',
                           method='GET', status=200),
              MockResponse(url='http://json-filtered/%3B/w4af.cmd%3B/w4af.cmd?'
                               'q=w4afExecToken%22%26%7C%0A',
                           body='    {"a":"w4afExecToken&|\n","b":"b"}',
                           content_type='application/javascript',
                           method='GET', status=200),
              ]

    def test_not_found_json(self):
        cfg = RUN_CONFIG['cfg']
        self._scan(self.target_url, cfg['plugins'])
        vulns = self.kb.get('rfd', 'rfd')
        self.assertEqual(0, len(vulns))


class TestJSONP(PluginTest):

    target_url = 'http://jsonp/?callback=rfd'

    MOCK_RESPONSES = [
          MockResponse(url='http://jsonp/?callback=rfd',
                       body=b'empty body',
                       content_type='application/json',
                       method='GET', status=200),
          MockResponse(url='http://jsonp/%3B/w4af.cmd%3B/w4af.cmd?callback'
                           '=rfd',
                       body='    rfd({ "Result": '
                            '{ "Timestamp": 1417601045 } }) ',
                       content_type='application/javascript',
                       method='GET', status=200),
          MockResponse(url='http://jsonp/%3B/w4af.cmd%3B/w4af.cmd?callback'
                           '=w4afExecToken',
                       body='    w4afExecToken({ "Result": '
                            '{ "Timestamp": 1417601045 } }) ',
                       content_type='application/javascript',
                       method='GET', status=200),
                      ]

    def test_found_jsonp(self):
        cfg = RUN_CONFIG['cfg']
        self._scan(self.target_url, cfg['plugins'])
        vulns = self.kb.get('rfd', 'rfd')
        self.assertEqual(1, len(vulns))
