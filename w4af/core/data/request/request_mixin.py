"""
request_mixin.py

Copyright 2010 Andres Riancho

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
import abc
import hashlib

from w4af.core.data.constants.encodings import DEFAULT_ENCODING
from w4af.core.data.misc.encoding import smart_unicode

CR = '\r'
LF = '\n'
CRLF = CR + LF
SP = ' '


class RequestMixIn(object):

    __slots__ = ()

    def dump(self, ignore_headers=()):
        """
        :return: The HTTP request as it would be sent to the wire, with a minor
                 change, instead of using the path in the second token of the
                 request we use the URL, this is just a user-friendly feature

                 Please note that we're returning a byte-string, with the
                 special characters in the headers and URL encoded as expected
                 by the RFC, and the POST-data (potentially) holding raw bytes
                 such as an image content.
        """
        data = ''
        if hasattr(self, 'data'):
            data = self.data
        elif hasattr(self, 'get_data'):
            data = self.get_data()
        if data is None:
            data = ''

        request_head = self.dump_request_head(ignore_headers=ignore_headers)

        return '%s%s%s' % (smart_unicode(request_head), CRLF, smart_unicode(data))

    @abc.abstractmethod
    def get_method(self):
        pass

    @abc.abstractmethod
    def get_uri(self):
        pass

    @abc.abstractmethod
    def get_headers(self):
        pass

    def get_request_hash(self, ignore_headers=()):
        """
        :return: Hash the request (as it would be sent to the wire) and return
        """
        return hashlib.md5(self.dump(ignore_headers=ignore_headers).encode(DEFAULT_ENCODING)).hexdigest()

    def get_request_line(self):
        """
        :return: request first line as sent to the wire.
        """
        return '%s %s HTTP/1.1%s' % (self.get_method(),
                                      self.get_uri().url_encode(),
                                      CRLF)

    def dump_request_head(self, ignore_headers=()):
        """
        :return: A string with the head of the request
        """
        return '%s%s' % (self.get_request_line(),
                          self.dump_headers(ignore_headers=ignore_headers))

    def dump_headers(self, ignore_headers=()):
        """
        :return: A string representation of the headers.
        """
        try:
            # For FuzzableRequest
            headers = self.get_all_headers()
        except AttributeError:
            # For HTTPRequest
            headers = self.get_headers()

        # Ignore the headers specified in the kwarg parameter
        for header_name in ignore_headers:
            try:
                headers.idel(header_name)
            except KeyError:
                # That's fine, if it doesn't exist we just continue
                continue

        return str(headers)
