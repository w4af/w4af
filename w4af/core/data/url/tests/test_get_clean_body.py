# -*- coding: utf-8 -*-
"""
test_get_clean_body.py

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
import urllib.request, urllib.parse, urllib.error

from w4af.core.data.url.helpers import get_clean_body, apply_multi_escape_table
from w4af.core.data.misc.web_encodings import SPECIAL_CHARS
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.fuzzer.mutants.tests.test_mutant import FakeMutant


class TestGetCleanBody(unittest.TestCase):
    def test_get_clean_body_simple(self):
        payload = 'payload'

        body = 'abc %s def' % payload
        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        clean_body = get_clean_body(mutant, response)

        self.assertEqual(clean_body, body.replace(payload, ''))
        self.assertIsInstance(clean_body, str)

    def test_get_clean_body_upper_lower(self):
        payload = 'PayLoaD'

        body = 'abc %s def' % payload
        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        clean_body = get_clean_body(mutant, response)

        self.assertEqual(clean_body, body.replace(payload, ''))
        self.assertIsInstance(clean_body, str)

    def test_get_clean_body_encoded(self):
        payload = 'hello/world'

        body = 'abc %s def' % urllib.parse.urlencode({'a': payload})
        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        clean_body = get_clean_body(mutant, response)

        self.assertEqual(clean_body, 'abc a= def')
        self.assertIsInstance(clean_body, str)

    def test_get_clean_body_encoded_upper_case(self):
        payload = 'hello/world'

        # uppercase here!
        body = 'abc %s def' % urllib.parse.urlencode({'a': payload})
        body = body.replace('%2f', '%2F')

        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        clean_body = get_clean_body(mutant, response)

        self.assertEqual(clean_body, 'abc a= def')
        self.assertIsInstance(clean_body, str)

    def test_get_clean_body_double_encoded(self):
        payload = 'hello/world'

        body = 'abc %s def' % urllib.parse.quote_plus(urllib.parse.quote_plus(payload))
        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        clean_body = get_clean_body(mutant, response)

        self.assertEqual(clean_body, 'abc  def')
        self.assertIsInstance(clean_body, str)

    def test_get_clean_body_encoded_find_special_char_fail(self):
        for char in SPECIAL_CHARS:
            payload = 'x%sy' % char

            body = 'abc %s def' % urllib.parse.quote_plus(payload)
            url = URL('http://w4af.com')
            headers = Headers([('Content-Type', 'text/html')])
            response = HTTPResponse(200, body, headers, url, url, charset='utf-8')

            freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
            created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                        False, {})

            mutant = created_mutants[0]

            clean_body = get_clean_body(mutant, response)

            msg = 'Failed for payload %r and body %r'
            args = (payload, body)
            self.assertEqual(clean_body, 'abc  def', msg % args)
            self.assertIsInstance(clean_body, str)

    def test_get_clean_body_max_escape_count(self):
        # This payload has one of each special char that will be encoded
        payload = ' '.join(SPECIAL_CHARS)

        body = 'abc %s def' % urllib.parse.quote_plus(payload)
        url = URL('http://w4af.com')
        headers = Headers([('Content-Type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url)

        freq = FuzzableRequest(URL('http://w4af.com/?a=1'))
        created_mutants = FakeMutant.create_mutants(freq, [payload], [],
                                                    False, {})

        mutant = created_mutants[0]

        tests = [(False, 1),
                 (False, 3),
                 (True,  1000),
                 (True,  None)]

        for expected_result, max_escape_count in tests:
            clean_body = get_clean_body(mutant,
                                        response,
                                        max_escape_count=max_escape_count)

            self.assertIsInstance(clean_body, str)

            if expected_result:
                msg = 'Failed in round (%s - %s), clean body is: "%s"'
                args = (expected_result, max_escape_count, clean_body)
                self.assertEqual(clean_body, 'abc  def', msg % args)
            else:
                msg = 'Failed in round (%s - %s), clean body is: "%s"'
                args = (expected_result, max_escape_count, clean_body)
                self.assertEqual(clean_body, body, msg % args)


class TestApplyMultiEscapeTable(unittest.TestCase):

    maxDiff = None

    def test_apply_multi_escape_table_0(self):
        escaped = apply_multi_escape_table('abc')
        escaped = [i for i in escaped]

        expected = ['abc',
                    '%61%62%63',
                    '&#x61;&#x62;&#x63;',
                    '&#97;&#98;&#99;',
                    '&#097;&#098;&#099;',
                    '%2561%2562%2563',
                    '%25%36%31%25%36%32%25%36%33',
                    '%26#x61%3b%26#x62%3b%26#x63%3b',
                    '%26#97%3b%26#98%3b%26#99%3b',
                    '%26#097%3b%26#098%3b%26#099%3b',
                    '%26%23x61%3b%26%23x62%3b%26%23x63%3b',
                    '%26%2397%3b%26%2398%3b%26%2399%3b',
                    '%26%23097%3b%26%23098%3b%26%23099%3b',
                    '%26%23%78%36%31%3b%26%23%78%36%32%3b%26%23%78%36%33%3b',
                    '%26%23%39%37%3b%26%23%39%38%3b%26%23%39%39%3b',
                    '%26%23%30%39%37%3b%26%23%30%39%38%3b%26%23%30%39%39%3b']

        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_count(self):
        escaped = apply_multi_escape_table('abc def'.join(SPECIAL_CHARS))
        escaped = [i for i in escaped]

        self.assertEqual(len(escaped), 346)

    def test_apply_multi_escape_table_1(self):
        escaped = apply_multi_escape_table(' ')
        escaped = [i for i in escaped]

        expected = [' ',
                    '%20',
                    '+',
                    '&nbsp;',
                    '&#x20;',
                    '&#32;',
                    '&#032;',
                    '%2b',
                    '%2520',
                    '%25%32%30',
                    '%26nbsp%3b',
                    '%26#x20%3b',
                    '%26#32%3b',
                    '%26#032%3b',
                    '%26%23x20%3b',
                    '%26%2332%3b',
                    '%26%23032%3b',
                    '%26%6e%62%73%70%3b',
                    '%26%23%78%32%30%3b',
                    '%26%23%33%32%3b',
                    '%26%23%30%33%32%3b']

        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_2(self):
        escaped = apply_multi_escape_table(' &')
        escaped = [i for i in escaped]

        expected = [' &',
                    ' %26',
                    '%20%26',
                    '+%26',
                    '&nbsp;&amp;',
                    ' &amp;',
                    '&#x20;&#x26;',
                    '&#x20;&',
                    ' &#x26;',
                    '&#x20;&amp;',
                    '&#32;&#38;',
                    '&#32;&',
                    ' &#38;',
                    '&#32;&amp;',
                    '&#032;&#038;',
                    '&#032;&',
                    ' &#038;',
                    '&#032;&amp;',
                    '%2b%26',
                    '%20%2526',
                    '%2520%2526',
                    '%2b%2526',
                    '%20%25%32%36',
                    '%25%32%30%25%32%36',
                    '%2b%25%32%36',
                    '+%2526',
                    '+%25%32%36',
                    '%26nbsp%3b%26amp%3b',
                    ' %26amp%3b',
                    '%26#x20%3b%26#x26%3b',
                    '%26#x20%3b%26',
                    ' %26#x26%3b',
                    '%26#x20%3b%26amp%3b',
                    '%26#32%3b%26#38%3b',
                    '%26#32%3b%26',
                    ' %26#38%3b',
                    '%26#32%3b%26amp%3b',
                    '%26#032%3b%26#038%3b',
                    '%26#032%3b%26',
                    ' %26#038%3b',
                    '%26#032%3b%26amp%3b',
                    '%20%26amp%3b',
                    '%26%23x20%3b%26%23x26%3b',
                    '%26%23x20%3b%26',
                    '%20%26%23x26%3b',
                    '%26%23x20%3b%26amp%3b',
                    '%26%2332%3b%26%2338%3b',
                    '%26%2332%3b%26',
                    '%20%26%2338%3b',
                    '%26%2332%3b%26amp%3b',
                    '%26%23032%3b%26%23038%3b',
                    '%26%23032%3b%26',
                    '%20%26%23038%3b',
                    '%26%23032%3b%26amp%3b',
                    '%26%6e%62%73%70%3b%26%61%6d%70%3b',
                    '%20%26%61%6d%70%3b',
                    '%26%23%78%32%30%3b%26%23%78%32%36%3b',
                    '%26%23%78%32%30%3b%26',
                    '%20%26%23%78%32%36%3b',
                    '%26%23%78%32%30%3b%26%61%6d%70%3b',
                    '%26%23%33%32%3b%26%23%33%38%3b',
                    '%26%23%33%32%3b%26',
                    '%20%26%23%33%38%3b',
                    '%26%23%33%32%3b%26%61%6d%70%3b',
                    '%26%23%30%33%32%3b%26%23%30%33%38%3b',
                    '%26%23%30%33%32%3b%26',
                    '%20%26%23%30%33%38%3b',
                    '%26%23%30%33%32%3b%26%61%6d%70%3b',
                    '+%26amp%3b',
                    '+%26%23x26%3b',
                    '+%26%2338%3b',
                    '+%26%23038%3b',
                    '+%26%61%6d%70%3b',
                    '+%26%23%78%32%36%3b',
                    '+%26%23%33%38%3b',
                    '+%26%23%30%33%38%3b']

        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_len_1(self):
        escaped = apply_multi_escape_table('a&c', max_len=3)
        escaped = [i for i in escaped]

        expected = ['a&c']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_len_2(self):
        escaped = apply_multi_escape_table('a&', max_len=4)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_len_3(self):
        escaped = apply_multi_escape_table('a&', max_len=5)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_len_4(self):
        escaped = apply_multi_escape_table('a&', max_len=6)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26', '%61%26', 'a&amp;', 'a&#38;', '&#97;&', 'a%2526']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_count_1(self):
        escaped = apply_multi_escape_table('a&', max_count=3)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26', '%61%26']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_count_max_len_1(self):
        escaped = apply_multi_escape_table('a&', max_count=3, max_len=6)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26', '%61%26']
        self.assertEqual(escaped, expected)

    def test_apply_multi_escape_table_max_count_max_len_2(self):
        escaped = apply_multi_escape_table('a&', max_count=3, max_len=4)
        escaped = [i for i in escaped]

        expected = ['a&', 'a%26']
        self.assertEqual(escaped, expected)
