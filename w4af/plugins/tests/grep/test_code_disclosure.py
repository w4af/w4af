"""
test_code_disclosure.py

Copyright 2011 Andres Riancho

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

from itertools import repeat
from unittest.mock import patch

import w4af.core.data.kb.knowledge_base as kb

from w4af.plugins.tests.helper import LOREM
from w4af.plugins.grep.code_disclosure import code_disclosure
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.dc.headers import Headers
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL


class TestCodeDisclosurePlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = code_disclosure()
        kb.kb.cleanup(ignore_errors=True)

    def tearDown(self):
        self.plugin.end()
        kb.kb.cleanup(ignore_errors=True)

    def _build_request_response(self, body, url=None, headers=None, method=None):
        url = url or URL('http://www.w4af.com/')
        headers = headers or Headers([('content-type', 'text/html')])
        method = method or 'GET'

        request = FuzzableRequest(url, method=method)
        response = HTTPResponse(200, body, headers, url, url, _id=1)

        return request, response

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_ASP_code_disclosure(self, *args):
        body = 'header <% Response.Write("Hello World!") %> footer'
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 1)

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_PHP_code_disclosure(self, *args):
        body = 'header <?php echo $a; ?> footer'
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 1)

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_no_code_disclosure_blank(self, *args):
        body = ''
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 0)

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_no_code_disclosure(self, *args):
        body = LOREM
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 0)

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_no_code_disclosure_xml(self, *args):
        body = """
                <?xml version="1.0"?>
                <note>
                    <to>Tove</to>
                    <from>Jani</from>
                    <heading>Reminder</heading>
                    <body>Don't forget me this weekend!</body>
                </note>"""
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 0)

    @patch('w4af.plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_no_analysis_content_type(self, *args):
        body = 'header <? echo $a; ?> footer'
        request, response = self._build_request_response(body)

        self.plugin.grep(request, response)
        self.assertEqual(len(kb.kb.get('code_disclosure', 'code_disclosure')), 0)
