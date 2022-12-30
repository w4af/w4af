# -*- coding: utf-8 -*-
"""
token.py

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

from w4af.core.data.misc.encoding import smart_unicode, smart_str_ignore


class DataToken(object):
    def __init__(self, name, value, path):
        self._name = name
        self._value = self._original_value = self._payload = value
        self._path = path

    def get_path(self):
        return self._path

    def set_path(self, new_path):
        self._path = new_path

    def get_name(self):
        return self._name

    def get_value(self):
        """
        :return: The "serialized representation" of this object.
        :see: FileDataToken, the implementation there makes more sense.
        """
        return self._value

    def get_payload(self):
        """
        :return: The payload which was used to create this object.
        :see: FileDataToken.get_value vs. FileDataToken.get_payload, the
              implementation there makes more sense.
        """
        return self._payload

    def set_payload(self, new_payload):
        self._payload = new_payload

    def get_original_value(self):
        return self._original_value

    def set_original_value(self, new_orig_val):
        self._original_value = new_orig_val

    def set_value(self, new_value):
        self.set_payload(new_value)
        self._value = new_value

    def __repr__(self):
        return '<DataToken for %s: "%s">' % (self.get_path(),
                                             self.get_value())

    def __str__(self):
        return smart_unicode(self._value, on_error_guess=False)

    def __bytes__(self):
        return smart_str_ignore(self._value)

    def __eq__(self, other):
        if isinstance(other, DataToken):
            return (self.get_name() == other.get_name() and
                    self.get_value() == other.get_value() and
                    self.get_path() == other.get_path())

        elif isinstance(other, str):
            return self.get_value() == other

        elif other is None:
            return False
        else:
            raise RuntimeError('Can not compare %s with DataToken.' % other)

    def __reduce__(self):
        return (self.__class__,
                (self._name, self._value, self._path),
                {'_payload': self._payload,
                 '_original_value': self._original_value})

    def __getattr__(self, attr):
        # see if this object has attr
        # NOTE do not use hasattr, it goes into infinite recursion
        if attr in self.__dict__:
            # this object has it
            return getattr(self, attr)

        # proxy to the wrapped object
        return getattr(self._value, attr)

    def __deepcopy__(self, memo):
        res = self.__class__(
            copy.deepcopy(self._name, memo),
            copy.deepcopy(self._value, memo),
            copy.deepcopy(self._path, memo)
        )
        res._original_value = copy.deepcopy(self._original_value, memo)
        return res

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __len__(self):
        return len(str(self))

