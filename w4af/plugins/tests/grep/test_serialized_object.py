"""
test_serialized_object.py

Copyright 2018 Andres Riancho

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
import unittest
import base64

import w4af.core.data.kb.knowledge_base as kb

from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.data.dc.query_string import QueryString
from w4af.core.data.dc.urlencoded_form import URLEncodedForm
from w4af.core.data.fuzzer.fuzzer import create_mutants
from w4af.plugins.grep.serialized_object import serialized_object
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse


SERIALIZED_PHP_OBJECTS = [
    b'O:8:"Example1":1:{s:10:"cache_file";s:15:"../../index.php";}',
    b'O:1:"a":1:{s:5:"value";s:3:"100";}',
]


class TestSerializedObject(unittest.TestCase):

    def setUp(self):
        kb.kb.cleanup(ignore_errors=True)

        self.plugin = serialized_object()

        self.url = URL('http://www.w4af.com/')
        self.headers = Headers([('content-type', 'text/html')])
        self.response = HTTPResponse(200, '', self.headers, self.url, self.url, _id=1)

    def tearDown(self):
        self.plugin.end()
        kb.kb.cleanup(ignore_errors=True)

    def test_php_serialized_objects_query_string(self):

        for i, obj in enumerate(SERIALIZED_PHP_OBJECTS):
            url = self.url.copy()

            qs = QueryString([(str(i), [obj])])
            url.set_querystring(qs)

            request = FuzzableRequest(url)

            self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 2)

    def test_php_serialized_objects_query_string_b64(self):
        url = self.url.copy()

        b64obj = base64.b64encode(SERIALIZED_PHP_OBJECTS[0])
        qs = QueryString([('viewstate', [b64obj])])
        url.set_querystring(qs)

        request = FuzzableRequest(url)

        self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 1)

    def test_php_serialized_objects_headers(self):
        headers = Headers([('X-API-Key', SERIALIZED_PHP_OBJECTS[0])])
        request = FuzzableRequest(self.url, headers=headers)

        self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 1)

    def test_php_serialized_objects_cookies(self):
        cookie_value = b'state=%s' % base64.b64encode(SERIALIZED_PHP_OBJECTS[0])
        headers = Headers([('Cookie', cookie_value)])
        request = FuzzableRequest(self.url, headers=headers)

        self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 1)

    def test_php_serialized_objects_post_data(self):
        post_data = b'obj=%s' % base64.b64encode(SERIALIZED_PHP_OBJECTS[1])
        headers = Headers([('Content-Type', 'application/x-www-form-urlencoded')])

        form = URLEncodedForm.from_postdata(headers, post_data)
        request = FuzzableRequest(self.url, headers=headers, post_data=form)

        self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 1)

    def test_not_php_serialized_objects(self):
        # Note that I'm sending the serialized object in reverse string order
        post_data = 'obj=%s' % base64.b64encode(SERIALIZED_PHP_OBJECTS[1][::-1])
        headers = Headers([('Content-Type', 'application/x-www-form-urlencoded')])

        form = URLEncodedForm.from_postdata(headers, post_data)
        request = FuzzableRequest(self.url, headers=headers, post_data=form)

        self.plugin.grep(request, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 0)

    def test_mutated_request(self):
        # Note that I'm sending the serialized object in reverse string order
        post_data = b'test=1&obj=%s' % base64.b64encode(SERIALIZED_PHP_OBJECTS[1])
        headers = Headers([('Content-Type', 'application/x-www-form-urlencoded')])

        form = URLEncodedForm.from_postdata(headers, post_data)
        request = FuzzableRequest(self.url, headers=headers, post_data=form)
        mutants = create_mutants(request, ['x'])

        for mutant in mutants:
            self.plugin.grep(mutant, self.response)

        self.assertEqual(len(kb.kb.get('serialized_object',
                                        'serialized_object')), 1)


RUN_CONFIGS = {
    'cfg': {
        'target': None,
        'plugins': {
            'grep': (PluginConfig('serialized_object'),),
            'crawl': (
                PluginConfig('web_spider',
                             ('only_forward', True, PluginConfig.BOOL)),
            )

        }
    }
}


class TestSerializedObjectIntegration(PluginTest):

    target_url = 'http://mock/'

    html = (b'<form action="/form" method="GET">'
            b'<input type="hidden" name="viewstate" value="%s">'
            b'</form>'
            % base64.b64encode(SERIALIZED_PHP_OBJECTS[0]))

    MOCK_RESPONSES = [MockResponse(url='http://mock/',
                                   body=html,
                                   method='GET', status=200),

                      MockResponse(url='http://mock/form',
                                   body='Ok',
                                   method='GET', status=200)]

    def test_vuln_found(self):
        self._scan(self.target_url, RUN_CONFIGS['cfg']['plugins'])

        vulns = self.kb.get('serialized_object',
                            'serialized_object')

        expected_vulns = {('Serialized object',
                           'A total of 1 HTTP requests contained a serialized object'
                           ' in the parameter with name "viewstate". The first ten'
                           ' matching URLs are:\n - http://mock/form\n')}

        vulns_set = set()

        for vuln in vulns:
            desc = vuln.get_desc(with_id=False)
            vulns_set.add((vuln.get_name(), desc))

        self.assertEqual(expected_vulns, vulns_set)
