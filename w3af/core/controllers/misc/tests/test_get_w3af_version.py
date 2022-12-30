# -*- encoding: utf-8 -*-
"""
test_get_w4af_version.py

Copyright 2015 Andres Riancho

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

from w4af.core.controllers.misc.get_w4af_version import (get_w4af_version_as_dict,
                                                         get_minimalistic_version,
                                                         get_w4af_version)


class TestGetVersion(unittest.TestCase):
    def test_trivial(self):
        self.assertIn(get_minimalistic_version(), get_w4af_version())

    def test_minimal(self):
        self.assertTrue(get_minimalistic_version().startswith('2019'))

    def test_dict(self):
        version_dict = get_w4af_version_as_dict()
        self.assertIn('version', version_dict)
        self.assertIn('revision', version_dict)
        self.assertIn('branch', version_dict)
        self.assertIn('dirty', version_dict)

