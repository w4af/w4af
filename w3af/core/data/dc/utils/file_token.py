# -*- coding: utf-8 -*-
"""
file_token.py

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
import copy

import w4af.core.data.kb.config as cf

from w4af.core.data.constants.file_templates.file_templates import get_template_with_payload
from w4af.core.data.dc.utils.token import DataToken
from w4af.core.controllers.misc.io import NamedBytesIO


class FileDataToken(DataToken):
    def __init__(self, name, value, filename, path):
        super(FileDataToken, self).__init__(name, value, path)

        default_extension = cf.cf.get('fuzzed_files_extension', 'gif')

        if filename is None:
            extension = default_extension
        else:
            extension = filename.rsplit('.', 1)[-1]
            extension = extension or default_extension

        self._extension = extension
        self._filename = filename
        self._payload = ''
        self._original_value = self._value = self.build_file(value)

    def get_payload(self):
        """
        :return: The payload which was used to create this object.
        :see: DataToken.get_value to understand the difference.
        """
        return self._payload

    def build_file(self, value):
        #
        # We don't want to create a new file if value is already a NamedStringIO
        # but if it is a string, we should create a new NamedStringIO instance
        # and return it
        #
        # The last "not isinstance" is important due to the fact that
        # NamedStringIO is a basestring subclass
        #
        if isinstance(value, str) and not isinstance(value, NamedBytesIO):
            _, file_content, fname = get_template_with_payload(self._extension,
                                                               value)

            # I have to create the NamedStringIO with a "name",
            # required for MultipartContainer to properly encode this as
            # multipart/post
            return NamedBytesIO(file_content, name=fname)

        return value

    def set_value(self, new_value):
        self.set_payload(new_value)
        self._value = self.build_file(new_value)

    def __reduce__(self):
        """
        Need to specify this because there is also a __reduce__ in DataToken
        and the FileDataToken implementation takes +1 parameter
        """
        args = (self._name, self._value, self._filename, self._path)
        return self.__class__, args, {'_payload': self._payload,
                                      '_original_value': self._original_value}

    def __deepcopy__(self, memo):
        res = self.__class__(
            copy.deepcopy(self._name, memo),
            copy.deepcopy(self._value, memo),
            copy.deepcopy(self._filename, memo),
            copy.deepcopy(self._path, memo)
        )
        res._original_value = copy.deepcopy(self._original_value, memo)
        res._payload = self._payload
        return res
