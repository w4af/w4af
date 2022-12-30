"""
detect.py

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
import string

from w4af.core.data.misc.encoding import smart_str_ignore

INTERESTING_NODEJS_STRINGS = ['\n', '{', '(']
INTERESTING_JAVA_STRINGS = ['java.util',
                            'java/util',
                            'java/lang/',
                            'reflect.annotation',
                            'com.sun.org.',
                            'org.jboss.',
                            'org.apache.',
                            'java.rmi.',
                            'javax/',
                            'com/sun/']
INTERESTING_NET_STRINGS = ['mscorlib',
                           'System.Data',
                           'System.Collections',
                           'Int32',
                           'System.Windows',
                           '$type',
                           'MethodName',
                           'PublicKeyToken']


def is_pickled_data(data):
    """
    :param data: Some data that we see on the application
    :return: True if the data looks like a python pickle
    """
    # pickle after version 2 starts with protocol opcode
    # and ends in '.' : http://formats.kaitai.io/python_pickle/
    if data.startswith(bytes([0x80])) and data.endswith(b'.'):
        return True

def is_java_serialized_data(data):
    """
    :param data: Some data that we see on the application
    :return: True if the data looks like a java serialized object
    """
    # All java serialized objects I've seen have non-printable chars
    has_binary = False

    for c in smart_str_ignore(data):
        if chr(c) not in string.printable:
            has_binary = True
            break

    if not has_binary:
        return False

    for interesting_string in [ smart_str_ignore(x) for x in INTERESTING_JAVA_STRINGS ]:
        if interesting_string in data:
            return True

    return False


def is_nodejs_serialized_data(data):
    """
    :param data: Some data that we see on the application
    :return: True if the data looks like a nodejs serialized object
    """
    for interesting_string in [ smart_str_ignore(x) for x in INTERESTING_NODEJS_STRINGS ]:
        if interesting_string in data:
            return True

    return False


def is_net_serialized_data(data):
    """
    :param data: Some data that we see on the application
    :return: True if the data looks like a .NET serialized object
    """
    for interesting_string in [ smart_str_ignore(x) for x in INTERESTING_NET_STRINGS ]:
        if interesting_string in data:
            return True

    return False
