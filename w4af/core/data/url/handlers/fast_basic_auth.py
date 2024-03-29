"""
FastHTTPBasicAuthHandler.py

Copyright 2006 Andres Riancho

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
import urllib.request, urllib.error, urllib.parse
import base64

from w4af.core.data.misc.encoding import smart_str_ignore

class FastHTTPBasicAuthHandler(urllib.request.AbstractBasicAuthHandler,
                               urllib.request.BaseHandler):
    """
    The AbstractBasicAuthHandler only sends the basic HTTP credentials after
    receiving a 401 which makes scans much slower (1 returns 401, 1 with the
    credentials returns 200).
    
    Created this handler to always send the configured credentials. 
    """
    handler_order = 200  # response processing before HTTPEquivProcessor

    def http_request(self, request):
        if not request.use_basic_auth:
            return request

        # Add the headers for the authorization...
        user, pw = self.passwd.find_user_password(None, request.get_full_url())
        if pw is not None:
            raw = '%s:%s' % (user, pw)
            auth = 'Basic %s' % base64.b64encode(smart_str_ignore(raw)).strip()
            request.add_header('Authorization', auth)

        return request

    https_request = http_request
