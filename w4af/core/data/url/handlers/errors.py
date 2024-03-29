"""
errors.py

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
import urllib.request, urllib.error, urllib.parse


class ErrorHandler(urllib.request.HTTPDefaultErrorHandler):
    """
    A simple handler that assigns IDs to errors.
    """
    def http_error_default(self, req, resp, code, msg, hdrs):
        err = urllib.error.HTTPError(req.get_full_url(), code, msg, hdrs, resp)
        err.id = req.id
        raise err


class NoOpErrorHandler(urllib.request.HTTPErrorProcessor):
    """
    no-op, we want to handle HTTP errors (which for urllib2 are the ones
    which have 200 <= code < 300) the same way we handle the rest of the
    HTTP responses.
    """
    def http_response(self, request, response):
        return response

    https_response = http_response
