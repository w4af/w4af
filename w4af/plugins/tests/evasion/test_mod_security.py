"""
test_mod_security.py

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

from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.url.HTTPRequest import HTTPRequest
from w4af.plugins.evasion.mod_security import mod_security


class TestEvasion(unittest.TestCase):
    
    def test_no_modification(self):
        modsec = mod_security()

        u = URL('http://www.w4af.com/')
        r = HTTPRequest( u )
        self.assertEqual(modsec.modify_request( r ).url_object.url_string,
                         'http://www.w4af.com/')

    def test_no_post_data(self):
        modsec = mod_security()
        
        u = URL('http://www.w4af.com/')
        r = HTTPRequest( u, data='' )
        self.assertEqual(modsec.modify_request( r ).data, '')

    def test_urlencoded_post_data(self):
        modsec = mod_security()
        
        u = URL('http://www.w4af.com/')
        r = HTTPRequest( u, data='a=b' )
        self.assertEqual(modsec.modify_request( r ).data,
                         '\x00a=b')
        