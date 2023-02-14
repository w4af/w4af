"""
multi_in.py

Copyright 2017 Andres Riancho

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
from typing import List, Tuple, Any, Generator, Iterable

import ahocorasick

from w4af.core.data.constants.encodings import DEFAULT_ENCODING
from w4af.core.data.misc.encoding import smart_unicode


class MultiIn(object):
    def __init__(self, keywords_or_assoc: Iterable[str]|Iterable[Tuple[str, Any]]):
        """
        :param keywords_or_assoc: A list with all the strings that we want
        to match against one or more strings using the "query" function.

        This list might be:
            [str_1, str_2 ... , str_N]

        Or something like:
            [(str_1, obj1) , (str_2, obj2) ... , (str_N, objN)].

        In the first case, if a match is found this class will return:
            [str_N,]

        In the second case we'll return
            [[str_N, objN],]
        """
        self._keywords_or_assoc = keywords_or_assoc
        self._translator = dict()
        self._build()

    def _build(self):
        self._acora = ahocorasick.Automaton()
        for idx, item in enumerate(self._keywords_or_assoc):

            if isinstance(item, tuple):
                keyword = item[0]

                if keyword in self._translator:
                    raise ValueError('Duplicated keyword "%s"' % keyword)

                self._translator[keyword] = item[1:]

                self._acora.add_word(keyword, keyword)
            elif isinstance(item, str):
                self._acora.add_word(item, item)
            elif isinstance(item, bytes):
                keyword = item.decode(DEFAULT_ENCODING, ignore_errors=True)
                self._acora.add(item, keyword)
            else:
                raise ValueError('Can NOT build MultiIn with provided values.')
        self._acora.make_automaton()

    def query(self, target_str) -> Generator[Any, Any, List[str]|List[Tuple[str,Any]]]:
        """
        Run through all the keywords and identify them in target_str

        :param target_str: The target string where the keywords need to be match
        :yield: The matches (see __init__)
        """
        target_was_string = False
        if isinstance(target_str, str):
            target_was_string = True
        else:
            target_str = target_str.decode(DEFAULT_ENCODING)

        def unwrap(output):
            if target_was_string:
                if isinstance(output, bytes):
                    return output.decode(DEFAULT_ENCODING)
                elif isinstance(output, list):
                    return [ unwrap(a) for a in output ]
                return output
            else:
                if isinstance(output, str):
                    return output.encode(DEFAULT_ENCODING)
                elif isinstance(output, list):
                    return [ unwrap(a) for a in output ]

        seen = set()

        for end_index, match in self._acora.iter_long(target_str):
            if match in seen:
                continue

            seen.add(match)
            extra_data = self._translator.get(match, None)

            if extra_data is None:
                yield unwrap(match)
            else:
                all_data = [match]
                all_data.extend(extra_data)
                yield unwrap(all_data)

        return []
