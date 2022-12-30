# -*- coding: utf-8 -*-
"""
test_HTTPRequest.py

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
import unittest

import msgpack
import pytest

from w4af.core.data.url.HTTPRequest import HTTPRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.data.dc.utils.token import DataToken
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.misc.encoding import smart_str_ignore

@pytest.mark.smoke
class TestHTTPRequest(unittest.TestCase):

    def test_basic(self):
        u = URL('http://www.w4af.com')
        req = HTTPRequest(u)
        
        self.assertEqual(req.get_full_url(), 'http://www.w4af.com/')
        self.assertEqual(req.get_uri().url_string, 'http://www.w4af.com/')

    def test_to_from_dict(self):
        headers = Headers([('Host', 'www.w4af.com')])
        req = HTTPRequest(URL("http://www.w4af.com/"), data='spameggs',
                          headers=headers)

        msg = msgpack.dumps(req.to_dict())
        loaded_dict = msgpack.loads(msg)
        loaded_req = HTTPRequest.from_dict(loaded_dict)
        self.assertEqual(loaded_req, req)
        self.assertEqual(list(req.__dict__.values()),
                         list(loaded_req.__dict__.values()))

    def test_to_dict_msgpack_with_data_token(self):
        token = DataToken('Host', 'www.w4af.com', ('Host',))
        headers = Headers([('Host', token)])
        freq = FuzzableRequest(URL("http://www.w4af.com/"), headers=headers)

        req = HTTPRequest.from_fuzzable_request(freq)

        msgpack.dumps(req.to_dict())
            
    def test_dump_case01(self):
        expected = '\r\n'.join(['GET http://w4af.com/a/b/c.php HTTP/1.1',
                                'Hello: World',
                                '',
                                ''])
        u = URL('http://w4af.com/a/b/c.php')
        headers = Headers([('Hello', 'World')])
        req = HTTPRequest(u, headers=headers)
        
        self.assertEqual(req.dump(), expected)

    def test_dump_case02(self):
        expected = '\r\n'.join(['GET http://w4af.com/a/b/c.php HTTP/1.1',
                                 'Hola: Múndo',
                                 '',
                                 ''])
        u = URL('http://w4af.com/a/b/c.php')
        headers = Headers([('Hola', 'Múndo')])
        req = HTTPRequest(u, headers=headers)
        
        self.assertEqual(smart_str_ignore(req.dump()), expected.encode('utf-8'))
