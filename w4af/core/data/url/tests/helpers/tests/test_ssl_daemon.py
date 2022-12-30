"""
test_ssl_daemon.py

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
import socket
import ssl

from w4af.core.data.url.tests.helpers.ssl_daemon import RawSSLDaemon


class TestUpperDaemon(unittest.TestCase):
    """
    This is a unittest for the UpperDaemon which lives in ssl_daemon.py

    @author: Andres Riancho <andres . riancho | gmail . com>
    """
    def setUp(self):
        self.ssl_daemon = RawSSLDaemon()
        self.ssl_daemon.start()
        self.ssl_daemon.wait_for_start()

    def test_basic(self):
        sent = b'abc'

        hostname = 'localhost'
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, self.ssl_daemon.get_port())) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssock.sendall(sent)
                received = ssock.recv(3)

        self.assertEqual(received, sent.upper())

    def tearDown(self):
        self.ssl_daemon.shutdown()
