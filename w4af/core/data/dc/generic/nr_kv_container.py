# -*- coding: utf-8 -*-
"""
nr_kv_container.py

Copyright 2014 Andres Riancho

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
from functools import partial

from collections import OrderedDict

from w4af.core.data.misc.encoding import smart_unicode
from w4af.core.data.dc.generic.data_container import DataContainer
from w4af.core.data.constants.encodings import UTF8
from w4af.core.data.parsers.utils.encode_decode import urlencode
from w4af.core.data.dc.utils.token import DataToken
from w4af.core.data.dc.utils.filter_printable import filter_non_printable


ERR_MSG_NO_REP = 'Unsupported init_val "%s", expected format is [("b", "2")]'
ERR_MSG_NO_DUPLICATES = 'Unsupported init_val "%s", duplicate values are not allowed'

class RepeatedValueException(TypeError):
    pass

class NonRepeatKeyValueContainer(DataContainer, OrderedDict):
    """
    This class represents a data container for data which doesn't allow
    repeated parameter names.

    The DataContainer supports things like a=1&a=2 for query strings, but for
    example HTTP headers can't be repeated (by RFC) and thus we don't
    need any repeated parameter names.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """
    def __init__(self, init_val=(), encoding=UTF8):
        DataContainer.__init__(self, encoding=encoding)
        OrderedDict.__init__(self)

        if isinstance(init_val, NonRepeatKeyValueContainer):
            self.update(init_val)
        elif isinstance(init_val, dict):
            # we lose compatibility with other ordered dict types this way
            raise TypeError('Undefined order, cannot get items from dict')
        else:
            for item in init_val:
                try:
                    key, val = item
                except TypeError:
                    raise TypeError(ERR_MSG_NO_REP % init_val)

                if key in self:
                    raise RepeatedValueException(init_val)

                if not isinstance(val, (str, bytes, DataToken)):
                    raise TypeError(ERR_MSG_NO_REP % init_val)

                self[key] = val

    def __reduce__(self):
        """
        :return: Return state information for pickling
        """
        init_val = [[k, self[k]] for k in self]
        encoding = self.encoding

        token = self.token

        return self.__class__, (init_val, encoding), {'token': token}

    def __setstate__(self, state):
        self.token = state['token']

    def get_type(self):
        return 'Generic non-repeat key value container'

    def _to_str_with_separators(self, key_val_sep, pair_sep):
        """
        :return: Join all the values stored in this data container using the
                 specified separators.
        """
        lst = []

        # pylint: disable=E1133
        for k, v in list(self.items()):
            to_app = '%s%s%s' % (k, key_val_sep,
                                  smart_unicode(v, encoding=UTF8))
            lst.append(to_app)
        # pylint: enable=E1133

        return pair_sep.join(lst)

    def iter_setters(self):
        """
        :yield: Tuples containing:
                    * The name of this token as a string
                    * The token value
                    * The token path
                    * The setter to modify the value
        """
        # pylint: disable=E1133
        for k, v in list(self.items()):
            if self.token_filter((k,), v):
                yield k, v, (k,), partial(self.__setitem__, k)
        # pylint: enable=E1133

    def __str__(self):
        """
        Return string representation.

        :return: string representation of the DataContainer Object.
        """
        return urlencode(self, encoding=self.encoding)

    def __unicode__(self):
        """
        Return unicode representation
        """
        return self._to_str_with_separators('=', '&')

    def get_short_printable_repr(self):
        """
        :return: A string with a short printable representation of self
        """
        if len(filter_non_printable(str(self))) <= self.MAX_PRINTABLE:
            return filter_non_printable(str(self))

        if self.get_token() is not None:
            # I want to show the token variable and value in the output
            # pylint: disable=E1133
            for k, v in list(self.items()):
                if isinstance(v, DataToken):
                    dt_str = '%s=%s' % (filter_non_printable(v.get_name()),
                                        filter_non_printable(v.get_value()))
                    return '...%s...' % dt_str[:self.MAX_PRINTABLE]
            # pylint: enable=E1133
        else:
            # I'll simply show the first N parameter and values until the
            # MAX_PRINTABLE is achieved
            return filter_non_printable(str(self))[:self.MAX_PRINTABLE]
