"""
cert_auth.py

Copyright 2006 Andres Riancho

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
import urllib.request, urllib.error, urllib.parse
import http.client

import w4af.core.controllers.output_manager as om


class certHTTPSConnection(http.client.HTTPSConnection):
    """
    An HTTPSConnection abstraction for easy integration with urllib2.

    #FIXME: This file ain't used, because it wasn't actually working!
    """
    key_file = None
    cert_file = None

    def __init__(self, host, port=None):
        http.client.HTTPSConnection.__init__(
            self, host, port, self.key_file, self.cert_file)
        #om.out.debug('Called __init__ of certHTTPSConnection.')


class certHTTPSHandler(urllib.request.HTTPSHandler):
    """
    An https handler for urllib2 that knows what to do with cert and key files.
    """
    def __init__(self, debuglevel=0):
        urllib.request.HTTPSHandler.__init__(self, debuglevel)
        self._sslCertFile = None
        self._sslKeyFile = None
        om.out.debug('Called __init__ of certHTTPSHandler.')

    def get_ssl_key_file(self):
        """
        :return: A string with the SSL key path and filename.
        """
        return self._sslKeyFile

    def set_ssl_key_file(self, keyFile):
        """
        :param keyFile: A string with the SSL key path and filename.
        :return: None
        """
        self._sslKeyFile = keyFile

    def get_ssl_cert_file(self):
        """
        :return: A string with the SSL cert path and filename.
        """
        return self._sslCertFile

    def set_ssl_cert_file(self, file):
        """
        :param file: A string with the SSL cert path and filename.
        :return: None
        """
        self._sslCertFile = file

    def https_open(self, req):
        # Original
        #return self.do_open(httplib.HTTPSConnection, req)

        # My version :P
        certHTTPSConnection.cert_file = self.get_ssl_cert_file()
        certHTTPSConnection.key_file = self.get_ssl_key_file()
        return self.do_open(certHTTPSConnection, req)
