# -*- coding: UTF-8 -*-
"""
test_sgml.py

Copyright 2011 Andres Riancho

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
import time
import os

from w4af import ROOT_PATH
from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.html import HTMLParser
from w4af.core.data.parsers.doc.pdf import PDFParser
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.parsers.document_parser import (document_parser_factory,
                                                    DocumentParser)


def _build_http_response(body_content, content_type):
    headers = Headers()
    headers['content-type'] = content_type

    url = URL('http://w4af.com')

    return HTTPResponse(200, body_content, headers, url, url, charset='utf-8')


class TestDocumentParserFactory(unittest.TestCase):

    PDF_FILE = os.path.join(ROOT_PATH, 'core', 'data', 'parsers', 'doc',
                            'tests', 'data', 'links.pdf')
    
    HTML_FILE = os.path.join(ROOT_PATH, 'core', 'data', 'parsers', 'doc',
                             'tests', 'data', 'sharepoint-pl.html')

    def test_html_ok(self):
        mime_types = ['text/html', 'TEXT/HTML', 'TEXT/plain',
                      'application/xhtml+xml']

        for mtype in mime_types:
            parser = document_parser_factory(_build_http_response('body', mtype))

            self.assertIsInstance(parser, DocumentParser)
            self.assertIsInstance(parser._parser, HTMLParser)
            self.assertEqual(parser.get_clear_text_body(), 'body')

    def test_html_upper(self):
        parser = document_parser_factory(_build_http_response('', 'TEXT/HTML'))

        self.assertIsInstance(parser, DocumentParser)
        self.assertIsInstance(parser._parser, HTMLParser)

    def test_pdf_case01(self):
        with open(self.PDF_FILE, "rb") as f:
            parser = document_parser_factory(
                    _build_http_response(f.read(),
                                        'application/pdf'))

        self.assertIsInstance(parser, DocumentParser)
        self.assertIsInstance(parser._parser, PDFParser)

    def test_no_parser(self):
        mime_types = ['application/bar', 'application/zip', 'video/abc',
                      'image/jpeg']

        for mtype in mime_types:
            response = _build_http_response('body', mtype)
            self.assertRaises(BaseFrameworkException, document_parser_factory,
                              response)

    def test_no_parser_binary(self):
        all_chars = ''.join([chr(i) for i in range(0,255)])
        response = _build_http_response(all_chars, 'application/bar')
        self.assertRaises(BaseFrameworkException, document_parser_factory,
                          response)
        
    def test_issue_106_invalid_url(self):
        """
        Issue to verify https://github.com/andresriancho/w3af/issues/106
        """
        with open(self.HTML_FILE) as f:
            sharepoint_pl = f.read()
        parser = document_parser_factory(_build_http_response(sharepoint_pl,
                                                              'text/html'))

        self.assertIsInstance(parser, DocumentParser)
        self.assertIsInstance(parser._parser, HTMLParser)
        
        paths = []
        paths.extend(url.get_path_qs() for url in parser.get_references()[0])
        paths.extend(url.get_path_qs() for url in parser.get_references()[1])
        
        expected_paths = {'/szukaj/_vti_bin/search.asmx',
                          '/_vti_bin/search.asmx?disco='}
        
        self.assertEqual(expected_paths, set(paths))
