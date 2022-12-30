"""
test_ntlm_auth.py

Copyright 2012 Andres Riancho

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
import urllib.request, urllib.error, urllib.parse

import pytest

from w4af.core.data.url.handlers.ntlm_auth import HTTPNtlmAuthHandler
from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http

@pytest.mark.w4af_moth
class TestNTLMHandler(unittest.TestCase):
    
    @pytest.mark.ci_fails
    def test_auth_valid_creds(self):
        url = get_w4af_moth_http("/w4af/core/ntlm_auth/ntlm_v1/")
        user = 'moth\\admin'
        password = 'admin'
    
        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, user, password)
        auth_NTLM = HTTPNtlmAuthHandler(passman)
    
        opener = urllib.request.build_opener(auth_NTLM)
    
        urllib.request.install_opener(opener)
    
        response = urllib.request.urlopen(url).read()
        self.assertTrue(response.startswith(b'You are admin from MOTH/'), response)
    
    def test_auth_invalid_creds(self):
        url = get_w4af_moth_http("/w4af/core/ntlm_auth/ntlm_v1/")
        user = 'moth\\invalid'
        password = 'invalid'
    
        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, user, password)
        auth_NTLM = HTTPNtlmAuthHandler(passman)
    
        opener = urllib.request.build_opener(auth_NTLM)
    
        urllib.request.install_opener(opener)
    
        self.assertRaises(urllib.error.URLError, urllib.request.urlopen, url)

    def test_auth_invalid_proto(self):
        url = get_w4af_moth_http("/w4af/core/ntlm_auth/ntlm_v2/")
        user = 'moth\\admin'
        password = 'admin'
    
        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, user, password)
        auth_NTLM = HTTPNtlmAuthHandler(passman)
    
        opener = urllib.request.build_opener(auth_NTLM)
    
        urllib.request.install_opener(opener)
    
        self.assertRaises(urllib.error.URLError, urllib.request.urlopen, url)
    