"""
test_cache_control.py

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
import unittest
from unittest.mock import patch
from itertools import repeat

import w4af.core.data.kb.knowledge_base as kb
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.plugins.grep.cache_control import cache_control


class TestCacheControl(unittest.TestCase):

    def setUp(self):
        create_temp_dir()
        kb.kb.cleanup()
        self.plugin = cache_control()

    def tearDown(self):
        kb.kb.cleanup()

    def test_cache_control_http(self):
        """
        No cache control, but the content is not sensitive (sent over http) so
        no bug is stored in KB.
        """
        body = 'abc'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 0)

    def test_cache_control_images(self):
        """
        No cache control, but the content is not sensitive (is an image)
        so no bug is stored in KB.
        """
        body = 'abc'
        url = URL('https://www.w4af.com/image.png')
        headers = Headers([('content-type', 'image/jpeg')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 0)

    def test_cache_control_empty_body(self):
        """
        No cache control, but the content is not sensitive (since it is an
        empty string) so no bug is stored in KB.
        """
        body = ''
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 0)
        
    @patch('w4af.plugins.grep.cache_control.is_404', side_effect=repeat(False))
    def test_cache_control_correct_headers(self, *args):
        """
        Sensitive content with cache control headers so NO BUG is stored in KB.
        """
        body = 'abc'
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('Pragma', 'No-cache'),
                           ('Cache-Control', 'No-store')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 0)

    @patch('w4af.plugins.grep.cache_control.is_404', side_effect=repeat(False))
    def test_cache_control_correct_meta(self, *args):
        """
        Sensitive content with cache control meta tags so no bug is stored in KB.
        """
        body = 'abc'
        meta_1 = '<meta http-equiv="Pragma" content="no-cache">'
        meta_2 = '<meta http-equiv="Cache-Control" content="no-store">'
        html = '<html><head>%s%s</head><body>%s</body></html>'
        response_body = html % (meta_1, meta_2, body)
        
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, response_body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 0)

    @patch('w4af.plugins.grep.cache_control.is_404', side_effect=repeat(False))
    def test_cache_control_incorrect_headers(self, *args):
        """
        Sensitive content with INCORRECT cache control headers bug should be
        stored in KB.
        """
        body = 'abc'
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('Pragma', 'Cache'),
                           ('Cache-Control', 'Store')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 1)
        
    @patch('w4af.plugins.grep.cache_control.is_404', side_effect=repeat(False))
    def test_cache_control_no_headers(self, *args):
        """
        Sensitive content without cache control headers so bug is stored in KB.
        """
        body = 'abc'
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)
        
        self.plugin.grep(request, resp)
        self.plugin.end()
        
        infos = kb.kb.get('cache_control', 'cache_control')
        self.assertEqual(len(infos), 1)
        
        info = infos[0]
        self.assertEqual(info.get_name(), 'Missing cache control for HTTPS content')