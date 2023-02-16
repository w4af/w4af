"""
multi_re.py

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
import re
from typing import List, Tuple, Any, Generator, Iterable, Optional, Pattern, Match

import hyperscan
from w4af.core.data.constants.encodings import DEFAULT_ENCODING

class MultiRE(object):

    def __init__(self,
        regexes_or_assoc: Iterable[bytes|Tuple[bytes, Any]],
        re_compile_flags: int = 0,
        hint_len: int = 3):
        """
        :param re_compile_flags: The regular expression compilation flags

        :param hint_len: Use only hints larger than hint_len to speed-up the search.

        :param regexes_or_assoc: A list with all the regular expressions that
                                 we want to match against one or more strings
                                 using the "query" function.

                                This list might look like:
                                    [re_str_1, re_str_2 ... , re_str_N]

                                Or something like:
                                    [(re_str_1, obj1), ..., (re_str_N, objN)].

                                In the first case, if a match is found this class
                                will return:
                                    [(match_obj, re_str_N, compiled_regex),]

                                In the second case we'll return:
                                    [(match_obj, re_str_N, compiled_regex, objN),]
        """
        self._regexes_or_assoc = regexes_or_assoc
        self._re_compile_flags = re_compile_flags
        self._hint_len = hint_len
        self._translator = dict()
        self._re_cache = dict()
        self._original_re = dict()
        self._build()

    def _build(self):
        self._hyperscan = hyperscan.Database()

        regexps = []
        flags = []
        indexes = []
        for idx, item in enumerate(self._regexes_or_assoc):

            #
            #   First we compile all regular expressions and save them to
            #   the re_cache.
            #
            if isinstance(item, tuple):
                regex = item[0]
                self._re_cache[idx] = re.compile(regex, self._re_compile_flags)

                if regex in self._translator:
                    raise ValueError('Duplicated regex "%s"' % regex)

                self._translator[idx] = item[1]
            elif isinstance(item, bytes):
                regex = item
                self._re_cache[idx] = re.compile(regex, self._re_compile_flags)
            else:
                raise ValueError('Can NOT build MultiRE with provided values.')

            self._original_re[idx] = regex
            regexps.append(regex)
            flags.append(0)
            indexes.append(idx)

        self._hyperscan.compile(
            expressions=regexps, flags=flags, ids=indexes
        )

    def query(self, target_str: bytes) -> Generator[Tuple[Match, str, bytes, Optional[Any]], None, None]:
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
        target_str = target_str.lower()
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
            compiled_regex = self._re_cache[idx]

            matchobj = compiled_regex.search(target_str)
            if matchobj:
                matches.append(self._create_output(matchobj, idx, compiled_regex))

        self._hyperscan.scan(target_str, match_event_handler=on_match)

        yield from matches


    def _create_output(self, matchobj, idx: int, compiled_regex) -> Tuple[Match, str, Pattern, Optional[Any]]:
        extra_data = self._translator.get(idx, None)
        regexp = self._original_re[idx]

        if extra_data is None:
            return matchobj, regexp, compiled_regex, None
        else:
            return (matchobj, regexp, compiled_regex, extra_data)

def convert_iterables_to_bytes(
        item: str|Tuple[str, Any]
    ) -> bytes|Tuple[bytes, Any]:
    if isinstance(item, str):
        return item.encode(DEFAULT_ENCODING)
    else:
        return (item[0].encode(DEFAULT_ENCODING), item[1])

class MultiREUnicode(MultiRE):

    def __init__(self,
        regexes_or_assoc: Iterable[str|Tuple[str, Any]],
        re_compile_flags: int = 0,
        hint_len: int = 3):
        MultiRE.__init__(
            self,
            map(convert_iterables_to_bytes, regexes_or_assoc),
            re_compile_flags,
            hint_len)

    def query(self, target_str: str) -> Generator[str|Tuple[re.Match, str, str, Optional[Any]], None, None]:
        target_str_bytes = target_str.encode(DEFAULT_ENCODING)
        for item in MultiRE.query(self, target_str_bytes):
            if isinstance(item, bytes):
                yield item.decode(DEFAULT_ENCODING)
                continue
            yield (item[0], item[1].decode(DEFAULT_ENCODING), item[2], item[3])