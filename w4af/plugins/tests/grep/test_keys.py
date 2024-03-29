"""
test_keys.py

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
import os
import unittest

import w4af.core.data.kb.knowledge_base as kb

from w4af.plugins.grep.keys import keys
from w4af.core.data.dc.headers import Headers
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.kb.vuln import Vuln
from w4af.core.data.kb.info import Info
from w4af.plugins.tests.helper import PluginTest


class TestKeys(PluginTest):

    def setUp(self):
        self.plugin = keys()
        kb.kb.clear('keys', 'keys')

    def tearDown(self):
        self.plugin.end()        
        
    def test_private_key(self):
        body = '-----BEGIN PRIVATE KEY-----'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)
        
        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 1)
        self.assertEqual(type(data[0]), Vuln)

    def test_public_key(self):
        body = '-----BEGIN PUBLIC KEY-----'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)

        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 1)
        self.assertEqual(type(data[0]), Info)        

    def test_xml_key(self):
        body = '<RSAKeyValue>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)

        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 1)  

    def test_public_ecdsa_key(self):
        body = 'ecdsa-sha2-nistp256'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)

        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 1)
        self.assertEqual(type(data[0]), Info)        

    def test_multi_match(self):
        body = """
        -----BEGIN OPENSSH PRIVATE KEY----- ssh-ed25519
        ------------------------------test <RSAKeyValue> <PrivateKey>
        """
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)

        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 3)

    def test_no_match(self):
        body = '-----BEGIN-----ssh----- BEGIN PRIVATE PUBLIC KEY'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        response = HTTPResponse(200, body, headers, url, url, _id=1)
        request = FuzzableRequest(url, method='GET')
        self.plugin.grep(request, response)

        data = kb.kb.get('keys', 'keys')
        self.assertEqual(len(data), 0)
