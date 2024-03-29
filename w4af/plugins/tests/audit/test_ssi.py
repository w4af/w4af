"""
test_ssi.py

Copyright 2012 Andres Riancho

This file is part of w4af, https://w4af.net/ .

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
import urllib.request, urllib.parse, urllib.error
from jinja2 import Template

from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse
from w4af.core.data.parsers.doc.url import URL


test_config = {
    'audit': (PluginConfig('ssi'),),
    'crawl': (
        PluginConfig(
            'web_spider',
            ('only_forward', True, PluginConfig.BOOL)),
    )
}


class TestSSI(PluginTest):

    target_url = 'http://mock/ssi.simple?message='

    class SSIMockResponse(MockResponse):
        def get_response(self, http_request, uri, response_headers):
            uri = urllib.parse.unquote(uri)
            seeds = re.findall('[1-9]{5}', uri)

            if len(seeds) == 2:
                body = 'Contains evaluated user input %s%s' % tuple(seeds)
            else:
                body = 'A regular body'

            return self.status, response_headers, body

    MOCK_RESPONSES = [SSIMockResponse(re.compile('.*'), body=None,
                                      method='GET', status=200)]

    def test_found_ssi(self):
        self._scan(self.target_url, test_config)
        vulns = self.kb.get('ssi', 'ssi')

        self.assertEqual(1, len(vulns), vulns)

        # Now some tests around specific details of the found vuln
        vuln = vulns[0]

        self.assertEqual('message', vuln.get_token_name())
        self.assertEqual('Server side include vulnerability', vuln.get_name())
        self.assertEqual(URL(self.target_url).uri2url().url_string,
                          vuln.get_url().url_string)


class TestJinja2SSI(PluginTest):

    target_url = 'http://mock/ssi.simple?message='

    class SSIMockResponse(MockResponse):
        def get_response(self, http_request, uri, response_headers):
            uri = urllib.parse.unquote_plus(uri)
            template = Template('Hello' + uri)
            body = template.render()
            return self.status, response_headers, body

    MOCK_RESPONSES = [SSIMockResponse(re.compile('.*'), body=None,
                                      method='GET', status=200)]

    def test_found_ssi(self):
        self._scan(self.target_url, test_config)
        vulns = self.kb.get('ssi', 'ssi')

        self.assertEqual(1, len(vulns), vulns)

        # Now some tests around specific details of the found vuln
        vuln = vulns[0]

        self.assertEqual('message', vuln.get_token_name())
        self.assertEqual('Server side include vulnerability', vuln.get_name())
        self.assertEqual(URL(self.target_url).uri2url().url_string,
                          vuln.get_url().url_string)

