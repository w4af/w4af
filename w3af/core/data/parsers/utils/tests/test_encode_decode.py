# -*- coding: utf-8 -*-
"""
test_encode_decode.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import unittest
from urllib.parse import parse_qs

from w3af.core.data.parsers.utils.encode_decode import htmldecode, urlencode


class TestHTMLDecode(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(htmldecode('hola mundo'), 'hola mundo')

    def test_tilde(self):
        self.assertEqual(htmldecode('hólá múndó'), 'hólá múndó')

    def test_special_char(self):
        self.assertEqual(htmldecode('hola &#0443'), 'hola ƻ')

    def test_charref(self):
        self.assertEqual(htmldecode('hola mundo &#x41'), 'hola mundo A')

    def test_html_encoded(self):
        self.assertEqual(htmldecode('&aacute;'), 'á')

    def test_bug_trigger_case01(self):
        """
        u'í'.decode('utf-8')
        
        UnicodeEncodeError: 'ascii' codec can't encode character u'\xed' in
                            position 9745: ordinal not in range(128)
        """
        html = 'Aquí encontrará'
        self.assertEqual(htmldecode(html), html)
    
    def test_bug_trigger_case02(self):
        html_utf8_raw = 'Aqu\xc3\xad encontrar\xc3\xa1'
        html_unicode = 'Aqu\xc3\xad encontrar\xc3\xa1'.decode('utf-8')
        self.assertEqual(htmldecode(html_utf8_raw), html_unicode)

    def test_bug_trigger_case03(self):
        html = '\xed'
        self.assertEqual(htmldecode(html), html)

    def test_bug_trigger_case04(self):
        html = '\xed'
        self.assertEqual(htmldecode(html), html)

    def test_html_invalid_utf8_entity_encoded(self):
        """Test for invalid entity encoded chars"""
        samples = {
            'Valid ASCII': "a",
            'Valid 2 Octet Sequence': "&#xc3b1",
            'Invalid 2 Octet Sequence': "&#xc328",
            'Invalid Sequence Identifier': "&#xa0a1",
            'Valid 3 Octet Sequence': "&#xe282a1",
            'Invalid 3 Octet Sequence (in 2nd Octet)': "&#xe228a1",
            'Invalid 3 Octet Sequence (in 3rd Octet)': "&#xe28228",
            'Valid 4 Octet Sequence': "&#xf0908cbc",
            'Invalid 4 Octet Sequence (in 2nd Octet)': "&#xf0288cbc",
            'Invalid 4 Octet Sequence (in 3rd Octet)': "&#xf09028bc",
            'Invalid 4 Octet Sequence (in 4th Octet)': "&#xf0288c28",
            'Valid 5 Octet Sequence (but not Unicode!)': " &#xf8a1a1a1a1 ",
            'Valid 6 Octet Sequence (but not Unicode!)': " &#xfca1a1a1a1a1 ",
            'Invalid unicode FFFE': "&#xFFFE",
            'Invalid unicode FFFF': "&#xFFFF",
        }

        for desc, sample in samples.items():
            try:
                htmldecode(sample)
            except Exception as e:
                msg = 'Exception "%s" was raised when trying to htmldecode() a "%s".'
                self.assertTrue(False, msg % (e, desc))


class TestURLEncode(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(urlencode(parse_qs('a=1&a=c'), 'latin1'), 'a=1&a=c')

    def test_tilde_case01(self):
        self.assertEqual(urlencode(parse_qs('a=á&a=2'), 'latin1'), 'a=%E1&a=2')

    def test_tilde_case02(self):
        self.assertEqual(urlencode(parse_qs('a=á&a=2'), 'utf-8'), 'a=%C3%A1&a=2')

    def test_raises(self):
        self.assertRaises(TypeError, urlencode, 'a=b&c=d', 'utf-8')
