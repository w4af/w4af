# -*- coding: UTF-8 -*-
"""
test_javascript.py

Copyright 2014 Andres Riancho

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
import os

from w4af.core.data.parsers.doc.javascript import JavaScriptParser
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.url import URL


class TestJavaScriptParser(unittest.TestCase):

    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "pynarcissus", "tests", "data")

    def parse(self, filename):
        with open(os.path.join(self.DATA_PATH, filename)) as f:
            body = f.read()
        js_mime = 'text/javascript'
        hdrs = Headers(list({'Content-Type': js_mime}.items()))
        response = HTTPResponse(200, body, hdrs,
                                URL('http://moth/xyz/'),
                                URL('http://moth/xyz/'),
                                _id=1)

        parser = JavaScriptParser(response)
        parser.parse()
        return parser

    def test_false_positives(self):
        for filename in ('jquery.js', 'angular.js', 'test_1.js', 'test_2.js',
                         'test_3.js'):
            p = self.parse(filename)
            self.assertEqual(p.get_references(), ([], []))

    def test_relative(self):
        p = self.parse('test_4.js')
        expected = [], [URL('http://moth/eggs.html'),
                        URL('http://moth/spam.html')]
        self.assertEqual(p.get_references()[0], expected[0])
        self.assertEqual(set(p.get_references()[1]), set(expected[1]))

    def test_full(self):
        p = self.parse('test_full_url.js')
        expected = [], [URL('http://moth/eggs.html'),
                        URL('http://moth/spam.html')]
        self.assertEqual(p.get_references()[0], expected[0])
        self.assertEqual(set(p.get_references()[1]), set(expected[1]))
