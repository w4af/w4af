"""
test_ssl_wrapper.py

Copyright 2015 Andres Riancho

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
import OpenSSL
import ssl

from w4af.core.data.url.openssl_wrapper.ssl_wrapper import OpenSSLReformattedError


class TestSSLError(unittest.TestCase):
    def test_str_8663_1(self):
        """
        :see: https://github.com/andresriancho/w4af/issues/8663
        """
        e = Exception('Message')
        self.assertEqual(str(OpenSSLReformattedError(e)), 'Message')

    def test_str_8663_2(self):
        e = OpenSSL.SSL.Error('OpenSSL.SSL.Error Message')
        se = ssl.SSLError('ssl.SSLError Message', OpenSSLReformattedError(e))
        self.assertEqual(str(se), "('ssl.SSLError Message', OpenSSLReformattedError(Error('OpenSSL.SSL.Error Message')))")

    def test_str_8663_3(self):
        e = OpenSSL.SSL.Error('OpenSSL.SSL.Error Message')
        se = ssl.SSLError('ssl.SSLError Message', e)
        self.assertEqual(str(se), "('ssl.SSLError Message', Error('OpenSSL.SSL.Error Message'))")
