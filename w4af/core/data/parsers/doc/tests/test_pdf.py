# -*- coding: UTF-8 -*-
"""
test_pdf.py

Copyright 2011 Andres Riancho

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

from w4af import ROOT_PATH
from w4af.core.data.parsers.doc.pdf import pdf_to_text, PDFParser
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.url import URL


class TestPDF(unittest.TestCase):
    
    SIMPLE_SAMPLE = os.path.join(ROOT_PATH, 'core', 'data', 'parsers', 'doc',
                                 'tests', 'data', 'simple.pdf')
    LINKS_SAMPLE = os.path.join(ROOT_PATH, 'core', 'data', 'parsers', 'doc',
                                'tests', 'data', 'links.pdf')
    
    def test_pdf_to_text(self):
        with open(self.SIMPLE_SAMPLE, "rb") as f:
            text = pdf_to_text(f.read())
        self.assertIn('Hello', text)
        self.assertIn('World', text)

    def test_pdf_to_text_no_pdf(self):
        text = pdf_to_text(b'hello world')
        self.assertEqual('', text)
    
    def test_pdf_parser(self):
        with open(self.LINKS_SAMPLE, "rb") as f:
            body = f.read()
        hdrs = Headers(list({'Content-Type': 'application/pdf'}.items()))
        response = HTTPResponse(200, body, hdrs,
                                URL('http://moth/'),
                                URL('http://moth/'),
                                _id=1)        
        
        parser = PDFParser(response)
        parser.parse()
        parsed, re_refs = parser.get_references()
        
        self.assertEqual(parsed, [])
        self.assertEqual(re_refs, [URL('http://moth/pdf/')])
        self.assertEqual(parser.get_clear_text_body().strip(),
                         'http://moth/pdf/')
