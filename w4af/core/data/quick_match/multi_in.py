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
from typing import List, Tuple, Any, Generator, Iterable, Optional

import hyperscan

from w4af.core.data.constants.encodings import DEFAULT_ENCODING
from w4af.core.data.misc.encoding import smart_unicode
from w4af.core.data.quick_match.multi_re import MultiRE, MultiREUnicode


class MultiIn(MultiRE):
    def __init__(self,
        keywords_or_assoc: Iterable[bytes|Tuple[bytes, Any]]
        ):
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
        MultiRE.__init__(self, keywords_or_assoc, re_compile_flags=0, literal=True)

    def query(self, target_str: bytes) -> Generator[Tuple[bytes, Optional[Any]], None, None]:
        """
        Run through all the regular expressions and identify them in target_str.

        We'll only run the regular expressions if:
             * They do not have keywords
             * The keywords exist in the string

        :param target_str: The target string where the keywords need to be match
        :yield: (match_obj, re_str_N, compiled_regex)
        """
        #
        #   Match the regular expressions that have keywords and those
        #   keywords are found in the target string by acora
        #
        seen = set()
        matches = []

        def on_match(
            idx: int,
            from_: int,
            to: int,
            flags: int,
            context: Optional[Any] = None
        ) -> Optional[bool]:
            if idx in seen:
                return
            seen.add(idx)
            matches.append(self._create_output(idx))

        self._hyperscan.scan(target_str, match_event_handler=on_match)

        yield from matches

    def _create_output(self, idx: int) -> Tuple[str, str, Optional[Any]]:
        extra_data = self._translator.get(idx, None)
        regexp = self._original_re[idx]

        if extra_data is None:
            return regexp
        else:
            return regexp, extra_data

def convert_iterables_to_bytes(
        item: str|Tuple[str, Any]
    ) -> bytes|Tuple[bytes, Any]:
    if isinstance(item, str):
        return item.encode(DEFAULT_ENCODING)
    else:
        return (item[0].encode(DEFAULT_ENCODING), item[1])

class MultiInUnicode(MultiIn):

    def __init__(self,
        regexes_or_assoc: Iterable[str|Tuple[str, Any]],
        re_compile_flags: int = 0,
        literal=False):
        MultiIn.__init__(
            self,
            map(convert_iterables_to_bytes, regexes_or_assoc))

    def query(self, target_str: str) -> Generator[str|Tuple[str, Optional[Any]], None, None]:
        target_str_bytes = target_str.encode(DEFAULT_ENCODING)
        for item in MultiIn.query(self, target_str_bytes):
            if isinstance(item, bytes):
                yield item.decode(DEFAULT_ENCODING)
                continue
            yield item[0].decode(DEFAULT_ENCODING), item[1]