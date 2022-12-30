"""
test_mask_password.py

Copyright 2019 Andres Riancho

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

from w4af.core.data.misc.mask_password import mask_password_string


class TestMaskPassword(unittest.TestCase):
    def test_mask_long_password(self):
        self.assertEqual(mask_password_string('this-is-long'),
                         'thi%s' % ('*' * len('s-is-long'),))

    def test_mask_short_password(self):
        self.assertEqual(mask_password_string('sho'), '***')
