# -*- encoding: utf-8 -*-
"""
test_multiin.py

Copyright 2012 Andres Riancho

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
import types
import unittest
import itertools

from w4af.core.data.quick_match.multi_in import MultiIn
from w4af.core.data.fuzzer.utils import rand_number


class MultiInTest(unittest.TestCase):

    def test_is_generator(self):
        in_list = [b'123', b'456', b'789']
        imi = MultiIn(in_list)
        results = imi.query(b'456')
        self.assertIsInstance(results, types.GeneratorType)

    def test_dup(self):
        in_list = [b'123', b'456', b'789']
        imi = MultiIn(in_list)

        result = to_list(imi.query(b'456 456'))
        self.assertEqual(1, len(result))

    def test_simplest(self):
        in_list = [b'123', b'456', b'789']
        imi = MultiIn(in_list)

        result = to_list(imi.query(b'456'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'456', result[0])

        result = to_list(imi.query(b'789'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'789', result[0])

    def test_assoc_obj(self):
        in_list = [(b'123456', None), (b'abcdef', 1)]
        imi = MultiIn(in_list)

        result = to_list(imi.query(b'spam1234567890eggs'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'123456', result[0])

        result = to_list(imi.query(b'foo abcdef bar'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'abcdef', result[0][0])
        self.assertEqual(1, result[0][1])

    def test_special_char(self):
        in_list = [b'javax.naming.NameNotFoundException', b'7', b'8']
        imi = MultiIn(in_list)

        s = b'abc \\n javax.naming.NameNotFoundException \\n 123'
        result = to_list(imi.query(s))
        self.assertEqual(1, len(result))
        self.assertEqual(b'javax.naming.NameNotFoundException', result[0])

        in_list = [b'abc(def)', b'foo(bar)']
        imi = MultiIn(in_list)

        result = to_list(imi.query(b'foo abc(def) bar'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'abc(def)', result[0])

    def test_unicode(self):
        in_list = ['ñ'.encode("utf-8"), 'ý'.encode('utf-8')]
        imi = MultiIn(in_list)

        result = to_list(imi.query('abcn'.encode('utf-8')))
        self.assertEqual(0, len(result))

        result = to_list(imi.query('abcñ'.encode('utf-8')))
        self.assertEqual(1, len(result))
        self.assertEqual('ñ'.encode('utf-8'), result[0])

    def test_null_byte(self):
        in_list = [b'\x01']
        imi = MultiIn(in_list)

        result = to_list(imi.query(b'abc\x00\x01def'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'\x01', result[0])

    def test_very_large_multiin(self):

        # Change this to test larger sizes
        COUNT = 5000

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield str(a).encode('utf-8')

                a = int(a)
                b = int(rand_number(5))
                yield str(a * b).encode('utf-8')

        fixed_samples = [b'123', b'456', b'789']
        in_list = itertools.chain(fixed_samples, generator(COUNT))

        imi = MultiIn(in_list)

        result = to_list(imi.query(b'456'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'456', result[0])

    def test_dup_keys(self):

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield str(a).encode('utf-8')

                a = int(a)
                b = int(rand_number(5))
                yield str(a * b).encode('utf-8')

        fixed_samples_1 = [b'123', b'456']
        fixed_samples_2 = [b'123', b'456', b'789']
        in_list = itertools.chain(fixed_samples_1,
                                  generator(5000),
                                  fixed_samples_2)

        imi = MultiIn(in_list)

        result = to_list(imi.query(b'789'))
        self.assertEqual(1, len(result))
        self.assertEqual(b'789', result[0])

    def test_many_start_similar(self):

        prefix = b'0000000'

        def generator(count):
            for _ in range(count):
                a = rand_number(5)
                yield prefix + str(a).encode('utf-8')

        fixed_samples = [prefix + b'78912']
        in_list = itertools.chain(generator(5000),
                                  fixed_samples)

        imi = MultiIn(in_list)

        result = to_list(imi.query(prefix + b'78912'))
        self.assertEqual(1, len(result))
        self.assertEqual(prefix + b'78912', result[0])


def to_list(generator):
    return [_ for _ in generator]
