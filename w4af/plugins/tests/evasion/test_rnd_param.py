"""
test_rnd_param.py

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

from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.parsers.doc.url import parse_qs
from w4af.core.data.url.HTTPRequest import HTTPRequest
from w4af.plugins.evasion.rnd_param import rnd_param


class TestEvasion(unittest.TestCase):

    def setUp(self):
        self.eplugin = rnd_param()

    def test_add_when_empty(self):
        url = URL('http://www.w4af.com/')
        original_req = HTTPRequest(url)

        modified_req = self.eplugin.modify_request(original_req)
        self.assertEqual(len(modified_req.url_object.querystring), 14)

    def test_add_when_qs(self):
        url = URL('http://www.w4af.com/?id=1')
        original_req = HTTPRequest(url)

        modified_req = self.eplugin.modify_request(original_req)
        self.assertEqual(len(modified_req.url_object.querystring), 19)
        self.assertIn('id=1', str(modified_req.url_object.querystring))

    def test_add_when_qs_and_postdata(self):
        url = URL('http://www.w4af.com/?id=1')
        original_req = HTTPRequest(url, data='a=b')

        modified_req = self.eplugin.modify_request(original_req)
        self.assertEqual(len(modified_req.url_object.querystring), 19)
        self.assertIn('id=1', str(modified_req.url_object.querystring))
        
        data = parse_qs(modified_req.data)
        self.assertEqual(len(data), 18)
        self.assertIn('a=b', str(data))

        modified_qs = modified_req.url_object.querystring
        self.assertEqual(len(modified_qs), 19)
