# -*- coding: UTF-8 -*-
"""
test_generate_404_filename.py

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


import unittest

from w4af.core.controllers.core_helpers.not_found.generate_404 import generate_404_filename


class TestGenerate404Filename(unittest.TestCase):
    def test_404_generation(self):

        tests = [
            ('ab-23', 'ab-53'),
            ('abc-12', 'abc-21'),
            ('ab-23.html', 'ab-53.html'),
            ('a1a2', 'a1d2'),
            ('a1a2.html', 'a1d2.html'),
            ('hello.html', 'heolo.html'),
            ('r57_Mohajer22.php', 'r57_oMahejr22.php'),

            # overflow handling
            ('Z', 'iK2ZZ'),
        ]

        for fname, modfname in tests:
            self.assertEqual(generate_404_filename(fname), modfname)

    def test_404_generation_twice(self):
        self.assertEqual(generate_404_filename('Entries'), 'Entreis')
        self.assertEqual(generate_404_filename('Entries', seed=2), 'Enrteis')
        self.assertEqual(generate_404_filename('Entries', seed=3), 'nErteis')
