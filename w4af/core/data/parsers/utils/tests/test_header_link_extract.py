# -*- coding: utf-8 -*-
"""
test_header_link_extract.py

Copyright 2015 Andres Riancho

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

from w4af.core.data.parsers.utils.header_link_extract import headers_url_generator
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.dc.headers import Headers


def build_http_response(extra_headers):
    url = URL('http://www.w4af.net/')

    headers = Headers()
    for header_name, header_value in extra_headers:
        headers[header_name] = header_value

    return HTTPResponse(200, '', headers, url, url, charset='utf-8')


class TestHeaderURLGenerator(unittest.TestCase):

    def get_urls(self, headers):
        http_response = build_http_response(headers)
        return [u for u, _, _, _ in headers_url_generator(http_response, None)]

    def test_simple(self):
        self.assertEqual(self.get_urls([('Location', '/abc')]),
                         [URL('http://www.w4af.net/abc')])

    def test_empty(self):
        self.assertEqual(self.get_urls([]), [])

    def test_x_pingback(self):
        extra_headers = [('x-pingback', 'http://www.w4af.net/xmlrpc.php')]
        self.assertEqual(self.get_urls(extra_headers),
                         [URL('http://www.w4af.net/xmlrpc.php')])

    def test_link(self):
        extra_headers = [('link',
                          '<http://www.w4af.net/?p=4758>; rel=shortlink')]
        self.assertEqual(self.get_urls(extra_headers),
                         [URL('http://www.w4af.net/?p=4758')])

    def test_link_x_pingback(self):
        extra_headers = [('link',
                          '<http://www.w4af.net/?p=4758>; rel=shortlink'),
                         ('x-pingback', 'http://www.w4af.net/xmlrpc.php')]
        self.assertEqual(set(self.get_urls(extra_headers)),
                         {URL('http://www.w4af.net/?p=4758'),
                          URL('http://www.w4af.net/xmlrpc.php')})

    def test_set_cookie(self):
        extra_headers = [('set-cookie',
                          '__cfduid=...; path=/x; domain=.w4af.net; HttpOnly')]
        self.assertEqual(self.get_urls(extra_headers),
                         [URL('http://www.w4af.net/x')])

    def test_link_invalid_format(self):
        extra_headers = [('link', 'xyz')]
        self.assertEqual(self.get_urls(extra_headers), [])

    def test_set_cookie_invalid_format(self):
        extra_headers = [('set-cookie', 'xyz')]
        self.assertEqual(self.get_urls(extra_headers), [])

    def test_set_cookie_empty(self):
        extra_headers = [('set-cookie', '')]
        self.assertEqual(self.get_urls(extra_headers), [])

    def test_x_pingback_invalid(self):
        extra_headers = [('x-pingback', '')]
        self.assertEqual(self.get_urls(extra_headers), [])
