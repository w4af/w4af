"""
query_string.py

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
import w4af.core.data.parsers.utils.encode_decode as enc_dec

from w4af.core.data.constants.encodings import DEFAULT_ENCODING
from w4af.core.data.dc.generic.kv_container import KeyValueContainer
from w4af.core.data.dc.utils.token import DataToken

ERR_MSG = 'Unsupported value "%s", expected format is [u"2", u"abc"].'


class QueryString(KeyValueContainer):
    """
    This class represents a Query String.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """
    def __init__(self, init_val=(), encoding=DEFAULT_ENCODING):
        super(QueryString, self).__init__(init_val, encoding)

    def get_type(self):
        return 'Query string'

    def __str__(self):
        """
        :return: string representation of the QueryString object.
        """
        return enc_dec.urlencode(self, encoding=self.encoding, safe='')

    def __setitem__(self, key, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError(ERR_MSG % value)

        for sub_val in value:
            if not isinstance(sub_val, (str, bytes, DataToken)):
                raise TypeError(ERR_MSG % value)

        super(QueryString, self).__setitem__(key, value)
