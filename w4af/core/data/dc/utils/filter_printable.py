# -*- coding: utf-8 -*-
"""
filter_printable.py

Copyright 2014 Andres Riancho

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
import string
import copy

from w4af.core.data.misc.encoding import smart_str_ignore
from w4af.core.controllers.misc.io import NamedBytesIO


NON_PRINTABLE_REPLACE = '.'


def is_printable_chr(c):
    return chr(c) in string.printable

def smart_chr(c):
    if type(c) == str:
        return c
    return chr(c)

def filter_non_printable(_str):
    chars = []

    if isinstance(_str, NamedBytesIO):
        _str = copy.deepcopy(_str)
        _str.seek(0)
        _str = _str.read()

    for c in smart_str_ignore(_str):
        if is_printable_chr(c):
            chars.append(c)
        else:
            if not chars:
                chars.append(NON_PRINTABLE_REPLACE)

            elif chars[-1] != NON_PRINTABLE_REPLACE:
                chars.append(NON_PRINTABLE_REPLACE)

    return ''.join([ smart_chr(c) for c in chars ])
