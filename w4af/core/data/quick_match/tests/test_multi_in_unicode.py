# -*- encoding: utf-8 -*-
"""
test_multi_in_unicode.py

Copyright 2023 Arthur Taylor

This file is part of w4af, https://w4af.net/ .

w4af is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import types
import unittest
import itertools

from w4af.core.data.quick_match.multi_in import MultiInUnicode
from w4af.core.data.fuzzer.utils import rand_number


class MultiInUnicodeTest(unittest.TestCase):

    def test_is_generator(self):
        in_list = ['123', '456', '789']
        imi = MultiInUnicode(in_list)
        results = imi.query('456')
        self.assertIsInstance(results, types.GeneratorType)

    def test_dup(self):
        in_list = ['123', '456', '789']
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('456 456'))
        self.assertEqual(1, len(result))

    def test_simplest(self):
        in_list = ['123', '456', '789']
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('456'))
        self.assertEqual(1, len(result))
        self.assertEqual('456', result[0])

        result = to_list(imi.query('789'))
        self.assertEqual(1, len(result))
        self.assertEqual('789', result[0])

    def test_assoc_obj(self):
        in_list = [('123456', None), ('abcdef', 1)]
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('spam1234567890eggs'))
        self.assertEqual(1, len(result))
        self.assertEqual('123456', result[0])

        result = to_list(imi.query('foo abcdef bar'))
        self.assertEqual(1, len(result))
        self.assertEqual('abcdef', result[0][0])
        self.assertEqual(1, result[0][1])

    def test_special_char(self):
        in_list = ['javax.naming.NameNotFoundException', '7', '8']
        imi = MultiInUnicode(in_list)

        s = 'abc \\n javax.naming.NameNotFoundException \\n 123'
        result = to_list(imi.query(s))
        self.assertEqual(1, len(result))
        self.assertEqual('javax.naming.NameNotFoundException', result[0])

        in_list = ['abc(def)', 'foo(bar)']
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('foo abc(def) bar'))
        self.assertEqual(1, len(result))
        self.assertEqual('abc(def)', result[0])

    def test_unicode(self):
        in_list = ['ñ', 'ý']
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('abcn'))
        self.assertEqual(0, len(result))

        result = to_list(imi.query('abcñ'))
        self.assertEqual(1, len(result))
        self.assertEqual('ñ', result[0])

    def test_null_byte(self):
        in_list = ['\x01']
        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('abc\x00\x01def'))
        self.assertEqual(1, len(result))
        self.assertEqual('\x01', result[0])

    def test_very_large_multiin(self):

        # Change this to test larger sizes
        COUNT = 5000

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield a

                a = int(a)
                b = int(rand_number(5))
                yield str(a * b)

        fixed_samples = ['123', '456', '789']
        in_list = itertools.chain(fixed_samples, generator(COUNT))

        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('456'))
        self.assertEqual(1, len(result))
        self.assertEqual('456', result[0])

    def test_dup_keys(self):

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield a

                a = int(a)
                b = int(rand_number(5))
                yield str(a * b)

        fixed_samples_1 = ['123', '456']
        fixed_samples_2 = ['123', '456', '789']
        in_list = itertools.chain(fixed_samples_1,
                                  generator(5000),
                                  fixed_samples_2)

        imi = MultiInUnicode(in_list)

        result = to_list(imi.query('789'))
        self.assertEqual(1, len(result))
        self.assertEqual('789', result[0])

    def test_many_start_similar(self):

        prefix = '0000000'

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield prefix + a

        fixed_samples = [prefix + '78912']
        in_list = itertools.chain(generator(5000),
                                  fixed_samples)

        imi = MultiInUnicode(in_list)

        result = to_list(imi.query(prefix + '78912'))
        self.assertEqual(1, len(result))
        self.assertEqual(prefix + '78912', result[0])


def to_list(generator):
    return [_ for _ in generator]
