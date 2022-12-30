"""
base64_nopadding.py

Copyright 2018 Andres Riancho

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
import re
import base64
import binascii

from w4af.core.data.misc.encoding import smart_unicode, smart_str_ignore

BASE64_RE = re.compile(r'^(?:[a-zA-Z0-9+/]{4})*(?:[a-zA-Z0-9+/]{2}==|[a-zA-Z0-9+/]{3}=|[a-zA-Z0-9+/]{4})$')


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.
    """
    data = smart_str_ignore(data)
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'=' * (4 - missing_padding)
    return base64.decodebytes(data)


def is_base64(data):
    """
    Telling if a string is base64 encoded or not is hard. Simply decoding it
    with base64.b64decode will yield a lot of false positives (it successfully
    decodes strings with characters outside of the base64 RFC).

    :param data: A string we saw in the web application
    :return: True if data is a base64 encoded string
    """
    is_b64, _ = maybe_decode_base64(data)
    return is_b64


def maybe_decode_base64(data):
    """
    Telling if a string is base64 encoded or not is hard. Simply decoding it
    with base64.b64decode will yield a lot of false positives (it successfully
    decodes strings with characters outside of the base64 RFC).

    :param data: A string we saw in the web application
    :return: A tuple containing True and the decoded string if the data was a
             base64 encoded string. A tuple containing False and None if the
             data wasn't a base64 encoded string.
    """
    # At least for this plugin we want long base64 strings
    if len(data) < 16:
        return False, None

    if not BASE64_RE.match(smart_unicode(data)):
        return False, None

    try:
        decoded_data = decode_base64(data)
    except binascii.Error:
        return False, None

    return True, decoded_data
