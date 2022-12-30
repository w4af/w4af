"""
test_cmmap_bloom.py

Copyright 2012 Andres Riancho

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
import pytest

from bloom_filter2 import BloomFilter as CMmapFilter
from w4af.core.data.bloomfilter.tests.generic_filter_test import GenericFilterTest
from w4af.core.data.bloomfilter.wrappers import GenericBloomFilter


class TestCMmapBloomfilterLarge(GenericFilterTest):

    CAPACITY = 20000
    ERROR_RATE = 0.000001

    def setUp(self):
        super(TestCMmapBloomfilterLarge, self).setUp()
        temp_file = GenericBloomFilter.get_temp_file()
        self.filter = CMmapFilter(max_elements=self.CAPACITY, error_rate=self.ERROR_RATE, filename=(temp_file,-1))


@pytest.mark.smoke
class TestCMmapBloomfilterSmall(GenericFilterTest):

    CAPACITY = 500
    ERROR_RATE = 0.000001

    def setUp(self):
        super(TestCMmapBloomfilterSmall, self).setUp()
        temp_file = GenericBloomFilter.get_temp_file()
        self.filter = CMmapFilter(max_elements=self.CAPACITY, error_rate=self.ERROR_RATE, filename=(temp_file,-1))
