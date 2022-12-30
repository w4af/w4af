"""
test_full_width_encode.py

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
from w4af.plugins.evasion.full_width_encode import full_width_encode


class TestEvasion(unittest.TestCase):
    
    def test_no_modification(self):
        fwe = full_width_encode()

        u = URL('http://www.w4af.com/')
        r = HTTPRequest( u )
        self.assertEqual(fwe.modify_request( r ).url_object.url_string,
                         'http://www.w4af.com/')

    def test_modify_path_filename(self):
        fwe = full_width_encode()
        
        u = URL('http://www.w4af.com/hola-mundo')
        r = HTTPRequest( u )
        self.assertEqual(fwe.modify_request( r ).url_object.url_string,
                         'http://www.w4af.com/%uFF48%uFF4f%uFF4c%uFF41%uFF0d%uFF4d%uFF55%uFF4e%uFF44%uFF4f')

        #
        #    The plugins should not modify the original request
        #
        self.assertEqual(u.url_string,
                         'http://www.w4af.com/hola-mundo')
        
