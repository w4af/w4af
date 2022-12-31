"""
test_empty_request.py

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
import unittest

from w4af.core.data.request.empty_request import EmptyFuzzableRequest


class TestEmptyRequest(unittest.TestCase):
    def test_create_instance(self):
        efr = EmptyFuzzableRequest()

        self.assertEqual(efr.get_uri(), None)
        self.assertEqual(efr.get_url(), None)