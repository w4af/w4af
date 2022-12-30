# -*- coding: UTF-8 -*-
"""
test_sgml.py

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
import os
import pytest
import unittest
from functools import partial
from itertools import combinations
from random import choice


from w4af import ROOT_PATH
from w4af.core.data.parsers.doc.sgml import SGMLParser, Tag
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.url.tests.test_HTTPResponse import TEST_RESPONSES
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.tests.data.constants import *


def build_http_response(url, body_content, headers=Headers()):
    if 'content-type' not in headers:
        headers['content-type'] = 'text/html'
    return HTTPResponse(200, body_content, headers, url, url, charset='utf-8')


@pytest.mark.smoke
class TestSGMLParser(unittest.TestCase):

    url = URL('http://w4af.com')

    def test_get_emails_filter(self):
        resp = build_http_response(self.url, '')
        p = SGMLParser(resp)
        p._emails = {'a@w4af.com', 'foo@not.com'}

        self.assertEqual(p.get_emails(), {'a@w4af.com', 'foo@not.com'})

        self.assertEqual(p.get_emails(domain='w4af.com'), ['a@w4af.com'])
        self.assertEqual(p.get_emails(domain='not.com'), ['foo@not.com'])

    def test_extract_emails_blank(self):
        resp = build_http_response(self.url, '')
        p = SGMLParser(resp)

        self.assertEqual(p.get_emails(), set())

    def test_extract_emails_mailto(self):
        body = '<a href="mailto:abc@w4af.com">test</a>'
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()

        expected_res = {'abc@w4af.com'}
        self.assertEqual(p.get_emails(), expected_res)

    def test_extract_emails_mailto_dup(self):
        body = '<a href="mailto:abc@w4af.com">a</a>'\
               '<a href="mailto:abc@w4af.com">b</a>'
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()

        expected_res = {'abc@w4af.com'}
        self.assertEqual(p.get_emails(), expected_res)

    def test_extract_emails_mailto_not_dup(self):
        body = '<a href="mailto:abc@w4af.com">a</a>'\
               '<a href="mailto:abc_def@w4af.com">b</a>'
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()

        expected_res = {'abc@w4af.com', 'abc_def@w4af.com'}
        self.assertEqual(p.get_emails(), expected_res)

    def test_mailto_ignored_in_links(self):
        body = '<a href="mailto:abc@w4af.com">a</a>'
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()

        parsed, _ = p.references
        self.assertEqual(parsed, [])

    def test_mailto_subject_body(self):
        body = '<a href="mailto:abc@w4af.com?subject=testing out mailto'\
               '&body=Just testing">test</a>'
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()

        expected_res = {'abc@w4af.com'}
        self.assertEqual(p.get_emails(), expected_res)

    def test_parser_attrs(self):
        body_content = HTML_DOC % {'head': '', 'body': ''}
        p = SGMLParser(build_http_response(self.url, body_content))

        # Assert parser has these attrs correctly initialized
        self.assertFalse(getattr(p, '_inside_form'))
        self.assertFalse(getattr(p, '_inside_select'))
        self.assertFalse(getattr(p, '_inside_text_area'))
        self.assertFalse(getattr(p, '_inside_script'))

        self.assertEqual(set(), getattr(p, '_tag_and_url'))
        self.assertEqual([], getattr(p, '_forms'))
        self.assertEqual([], getattr(p, '_comments_in_doc'))
        self.assertEqual([], getattr(p, '_meta_redirs'))
        self.assertEqual([], getattr(p, '_meta_tags'))

    def test_baseurl(self):
        body = HTML_DOC % {'head': BASE_TAG, 'body': ''}
        resp = build_http_response(self.url, body)
        p = SGMLParser(resp)
        p.parse()
        self.assertEqual(URL('http://www.w4afbase.com/'), p._base_url)

    def test_meta_tags(self):
        body = HTML_DOC % {'head': META_REFRESH + META_REFRESH_WITH_URL,
                           'body': ''}
        resp = build_http_response(self.url, body)

        p = SGMLParser(resp)
        p.parse()

        self.assertEqual(2, len(p.meta_redirs))
        self.assertIn("2;url=http://crawler.w4af.com/", p.meta_redirs)
        self.assertIn("600", p.meta_redirs)
        self.assertEqual([URL('http://crawler.w4af.com/')], p.references[0])

    def test_meta_tags_with_single_quotes(self):
        body = HTML_DOC % {'head': META_REFRESH + META_REFRESH_WITH_URL_AND_QUOTES,
                           'body': ''}
        resp = build_http_response(self.url, body)

        p = SGMLParser(resp)
        p.parse()

        self.assertEqual(2, len(p.meta_redirs))
        self.assertIn("2;url='http://crawler.w4af.com/'", p.meta_redirs)
        self.assertIn("600", p.meta_redirs)
        self.assertEqual([URL('http://crawler.w4af.com/')], p.references[0])

    def test_case_sensitivity(self):
        """
        Ensure handler methods are *always* called with lowered-cased
        tag and attribute names
        """
        def islower(s):
            il = False
            if isinstance(s, str):
                il = s.islower()
            else:
                il = all(k.islower() for k in s)
            assert il, "'%s' is not lowered-case" % s
            return il

        def start_wrapper(orig_start, tag):
            islower(tag.tag)
            islower(tag.attrib)
            return orig_start(tag)

        tags = (A_LINK_ABSOLUTE, INPUT_CHECKBOX_WITH_NAME, SELECT_WITH_NAME,
                TEXTAREA_WITH_ID_AND_DATA, INPUT_HIDDEN)
        ops = "lower", "upper", "title"

        for indexes in combinations(list(range(len(tags))), 2):

            body_elems = []

            for index, tag in enumerate(tags):
                ele = tag
                if index in indexes:
                    ele = getattr(tag, choice(ops))()
                body_elems.append(ele)

            body = HTML_DOC % {'head': '', 'body': ''.join(body_elems)}
            resp = build_http_response(self.url, body)
            p = SGMLParser(resp)
            orig_start = p.start
            wrapped_start = partial(start_wrapper, orig_start)
            p.start = wrapped_start
            p.parse()

    def test_parsed_references(self):
        # The *parsed* urls *must* come both from valid tags and tag attributes
        # Also invalid urls like must be ignored (like javascript instructions)
        body = """
        <html>
            <a href="/x.py?a=1" Invalid_Attr="/invalid_url.php">
            <form action="javascript:history.back(1)">
                <tagX href="/py.py"/>
            </form>
        </html>"""
        r = build_http_response(self.url, body)
        p = SGMLParser(r)
        p.parse()
        parsed_refs = p.references[0]
        self.assertEqual(1, len(parsed_refs))
        self.assertEqual(
            'http://w4af.com/x.py?a=1', parsed_refs[0].url_string)

    def test_reference_with_colon(self):
        body = """
        <html>
            <a href="d:url.html?id=13&subid=3">foo</a>
        </html>"""
        r = build_http_response(self.url, body)
        p = SGMLParser(r)
        p.parse()
        parsed_refs = p.references[0]
        #
        #    Finding zero URLs is the correct behavior based on what
        #    I've seen in Opera and Chrome.
        #
        self.assertEqual(0, len(parsed_refs))

    def test_get_clear_text_body(self):
        html = 'header <b>ABC</b>-<b>DEF</b>-<b>XYZ</b> footer'
        clear_text = 'header ABC-DEF-XYZ footer'
        headers = Headers([('Content-Type', 'text/html')])
        r = build_http_response(self.url, html, headers)

        p = SGMLParser(r)
        p.parse()

        self.assertEqual(clear_text, p.get_clear_text_body())

    def test_get_clear_text_body_memoized(self):
        html = 'header <b>ABC</b>-<b>DEF</b>-<b>XYZ</b> footer'
        clear_text = 'header ABC-DEF-XYZ footer'
        headers = Headers([('Content-Type', 'text/html')])
        r = build_http_response(self.url, html, headers)

        p = SGMLParser(r)
        p.parse()

        calculated_clear_text = p.get_clear_text_body()
        self.assertEqual(clear_text, calculated_clear_text)

    def test_get_clear_text_body_encodings(self):

        pytest.skip('Not sure why this one is failing :S')

        for lang_desc, (body, encoding) in TEST_RESPONSES.items():
            encoding_header = 'text/html; charset=%s' % encoding
            headers = Headers([('Content-Type', encoding_header)])

            encoded_body = body.encode(encoding)
            r = build_http_response(self.url, encoded_body, headers)

            p = SGMLParser(r)
            p.parse()

            ct_body = p.get_clear_text_body()

            # These test strings don't really have tags, so they should be eq
            self.assertEqual(ct_body, body)

    def test_get_clear_text_issue_4402(self):
        """
        :see: https://github.com/andresriancho/w4af/issues/4402
        """
        test_file_path = 'core/data/url/tests/data/encoding_4402.php'
        test_file = os.path.join(ROOT_PATH, test_file_path)
        with open(test_file, "rb") as f:
            body = f.read()

        sample_encodings = [encoding for _, (_, encoding) in TEST_RESPONSES.items()]
        sample_encodings.extend(['', 'utf-8'])

        for encoding in sample_encodings:
            encoding_header = 'text/html; charset=%s' % encoding
            headers = Headers([('Content-Type', encoding_header)])

            r = build_http_response(self.url, body, headers)

            p = SGMLParser(r)
            p.parse()

            p.get_clear_text_body()


class TestTagsByFilter(unittest.TestCase):
    def test_basic(self):
        body = '<html><a href="/abc">foo</a></html>'
        url = URL('http://www.w4af.com/')
        headers = Headers()
        headers['content-type'] = 'text/html'
        resp = HTTPResponse(200, body, headers, url, url, charset='utf-8')

        p = SGMLParser(resp)
        tags = p.get_tags_by_filter(('a',), yield_text=True)
        tags = list(tags)

        self.assertEqual(tags, [Tag('a', {'href': '/abc'}, 'foo')])

    def test_two(self):
        body = '<html><a href="/abc">foo</a><b>bar</b></html>'
        url = URL('http://www.w4af.com/')
        headers = Headers()
        headers['content-type'] = 'text/html'
        resp = HTTPResponse(200, body, headers, url, url, charset='utf-8')

        p = SGMLParser(resp)
        tags = p.get_tags_by_filter(('a', 'b'), yield_text=True)
        tags = list(tags)

        self.assertEqual([Tag('a', {'href': '/abc'}, 'foo'),
                          Tag('b', {}, 'bar')], tags)

    def test_nested_with_text(self):
        body = '<html><a href="/abc">foo<div>bar</div></a></html>'
        url = URL('http://www.w4af.com/')
        headers = Headers()
        headers['content-type'] = 'text/html'
        resp = HTTPResponse(200, body, headers, url, url, charset='utf-8')

        p = SGMLParser(resp)
        tags = p.get_tags_by_filter(('a', 'b'), yield_text=True)
        tags = list(tags)

        self.assertEqual([Tag('a', {'href': '/abc'}, 'foo')], tags)

    def test_none(self):
        body = '<html><a href="/abc">foo<div>bar</div></a></html>'
        url = URL('http://www.w4af.com/')
        headers = Headers()
        headers['content-type'] = 'text/html'
        resp = HTTPResponse(200, body, headers, url, url, charset='utf-8')

        p = SGMLParser(resp)
        tags = p.get_tags_by_filter(None)
        tags = list(tags)
        tag_names = [tag.name for tag in tags]

        self.assertEqual(tag_names, ['html', 'body', 'a', 'div'])