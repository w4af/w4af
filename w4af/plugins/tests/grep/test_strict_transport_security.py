"""
test_strict_transport_security.py

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

import w4af.core.data.kb.knowledge_base as kb
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.plugins.grep.strict_transport_security import strict_transport_security


class TestSTSSecurity(unittest.TestCase):

    def setUp(self):
        create_temp_dir()
        self.plugin = strict_transport_security()

    def tearDown(self):
        self.plugin.end()
        kb.kb.cleanup()

    def test_http_no_vuln(self):
        body = ''
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)
        self.assertEqual(len(kb.kb.get('strict_transport_security',
                                        'strict_transport_security')), 0)

    def test_https_with_sts(self):
        body = ''
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('strict-transport-security',
                            'max-age=31536000; includeSubDomains; preload')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)
        self.assertEqual(len(kb.kb.get('strict_transport_security',
                                        'strict_transport_security')), 0)

    def test_https_without_sts(self):
        body = ''
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)

        findings = kb.kb.get('strict_transport_security',
                             'strict_transport_security')
        self.assertEqual(len(findings), 1, findings)

        info_set = findings[0]
        expected_desc = 'The remote web server sent 1 HTTPS responses which' \
                        ' do not contain the Strict-Transport-Security' \
                        ' header. The first ten URLs which did not send the' \
                        ' header are:\n - https://www.w4af.com/\n'

        self.assertEqual(info_set.get_id(), [1])
        self.assertEqual(info_set.get_desc(), expected_desc)
        self.assertEqual(info_set.get_name(),
                         'Missing Strict Transport Security header')

    def test_https_without_sts_group_by_domain(self):
        body = ''
        url = URL('https://www.w4af.com/1')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)

        body = ''
        url = URL('https://www.w4af.com/2')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=2)

        self.plugin.grep(request, resp)

        findings = kb.kb.get('strict_transport_security',
                             'strict_transport_security')
        self.assertEqual(len(findings), 1, findings)

        info_set = findings[0]
        expected_desc = 'The remote web server sent 2 HTTPS responses which' \
                        ' do not contain the Strict-Transport-Security' \
                        ' header. The first ten URLs which did not send the' \
                        ' header are:\n - https://www.w4af.com/1\n' \
                        ' - https://www.w4af.com/2\n'

        self.assertEqual(info_set.get_id(), [1, 2])
        self.assertEqual(info_set.get_desc(), expected_desc)
        self.assertEqual(info_set.get_name(),
                         'Missing Strict Transport Security header')
