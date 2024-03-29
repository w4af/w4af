"""
test_update_URLs_in_KB.py

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

import w4af.core.data.kb.knowledge_base as kb
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.request.fuzzable_request import FuzzableRequest


class TestUpdateURLs(unittest.TestCase):

    def setUp(self):
        kb.kb.cleanup()

    def test_basic(self):
        u1 = URL('http://w4af.net/')
        r1 = FuzzableRequest(u1, method='GET')
        kb.kb.add_fuzzable_request(r1)
        result = kb.kb.get_all_known_urls()
        self.assertEqual(len(result), 1)
        self.assertEqual("http://w4af.net/", list(result)[0].url_string)

        u2 = URL('http://w4af.net/blog/')
        r2 = FuzzableRequest(u2, method='GET')
        u3 = URL('http://w4af.net/')
        r3 = FuzzableRequest(u3, method='GET')
        kb.kb.add_fuzzable_request(r1)
        kb.kb.add_fuzzable_request(r2)
        kb.kb.add_fuzzable_request(r3)

        result = kb.kb.get_all_known_urls()
        self.assertEqual(len(result), 2)
        expected_set = set(["http://w4af.net/", "http://w4af.net/blog/"])
        self.assertEqual(expected_set,
                         set([u.url_string for u in result]))
