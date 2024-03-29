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

from itertools import repeat
from unittest.mock import patch

import w4af.core.data.kb.knowledge_base as kb

from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.plugins.grep.meta_generator import meta_generator


class TestMetaGenerator(unittest.TestCase):

    def setUp(self):
        kb.kb.cleanup()

        self.plugin = meta_generator()
        self.url = URL('http://www.w4af.com/')

    def _generate_response(self, body):
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, self.url, self.url, _id=1)
        return response

    def tearDown(self):
        self.plugin.end()

    @patch('w4af.plugins.grep.meta_generator.is_404', side_effect=repeat(False))
    def test_detects_meta_tags_with_generator(self, *args):
        request = FuzzableRequest(self.url)
        response = self._generate_response('<meta name="generator" content="wordpress 1.2.3">')

        self.plugin.grep(request, response)

        info_sets = kb.kb.get('meta_generator', 'content_generator')

        self.assertEqual(len(info_sets), 1)
        info_set = info_sets[0]

        self.assertEqual(info_set.get_url(), self.url)

        expected_desc = ('The application returned 1 HTTP responses containing the'
                         ' generator meta tag value "wordpress 1.2.3". The first'
                         ' ten URLs  that match are:\n - http://www.w4af.com/\n')
        self.assertEqual(info_set.get_desc(), expected_desc)

    @patch('w4af.plugins.grep.meta_generator.is_404', side_effect=repeat(False))
    def test_groups_findings(self, *args):
        request = FuzzableRequest(self.url)

        response_1 = self._generate_response('<meta name="generator" content="wordpress 1.2.3">')
        response_2 = self._generate_response('<meta name="generator" content="wordpress 1.2.4">')

        self.plugin.grep(request, response_1)
        self.plugin.grep(request, response_2)

        info_sets = kb.kb.get('meta_generator', 'content_generator')

        self.assertEqual(len(info_sets), 2)

        urls = set(i.get_url() for i in info_sets)
        descs = set(i.get_desc() for i in info_sets)

        self.assertEqual(urls, {self.url, self.url})

        expected_desc_1 = ('The application returned 1 HTTP responses containing the'
                           ' generator meta tag value "wordpress 1.2.3". The first'
                           ' ten URLs  that match are:\n - http://www.w4af.com/\n')

        expected_desc_2 = ('The application returned 1 HTTP responses containing the'
                           ' generator meta tag value "wordpress 1.2.4". The first'
                           ' ten URLs  that match are:\n - http://www.w4af.com/\n')

        self.assertEqual(descs, {expected_desc_1, expected_desc_2})

    @patch('w4af.plugins.grep.meta_generator.is_404', side_effect=repeat(False))
    def test_avoid_false_positive_0(self, *args):
        request = FuzzableRequest(self.url)
        response = self._generate_response('<meta name="not-a-generator" content="wordpress 1.2.3">')

        self.plugin.grep(request, response)

        info_sets = kb.kb.get('meta_generator', 'content_generator')

        self.assertEqual(len(info_sets), 0)

    @patch('w4af.plugins.grep.meta_generator.is_404', side_effect=repeat(False))
    def test_avoid_false_positive_1(self, *args):
        request = FuzzableRequest(self.url)
        response = self._generate_response('<meta name="generator">')

        self.plugin.grep(request, response)

        info_sets = kb.kb.get('meta_generator', 'content_generator')

        self.assertEqual(len(info_sets), 0)

    @patch('w4af.plugins.grep.meta_generator.is_404', side_effect=repeat(False))
    def test_avoid_false_positive_2(self, *args):
        request = FuzzableRequest(self.url)
        response = self._generate_response('<meta name="generator" name="">')

        self.plugin.grep(request, response)

        info_sets = kb.kb.get('meta_generator', 'content_generator')

        self.assertEqual(len(info_sets), 0)
