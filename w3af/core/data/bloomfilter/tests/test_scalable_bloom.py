"""
test_scalable_bloom.py

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

from w4af.core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from w4af.core.data.bloomfilter.tests.generic_filter_test import GenericFilterTest
from w4af.core.data.bloomfilter.seekfile_bloom import FileSeekBloomFilter
from w4af.core.data.bloomfilter.wrappers import GenericBloomFilter


class WrappedFileSeekBloomFilter(GenericBloomFilter):
    def __init__(self, capacity, error_rate):
        """
        :param capacity: How many items you want to store, eg. 10000
        :param error_rate: The acceptable false positive rate, eg. 0.001
        """
        GenericBloomFilter.__init__(self, capacity, error_rate)

        temp_file = self.get_temp_file()
        self.bf = FileSeekBloomFilter(capacity, error_rate, temp_file)

    def close(self):
        self.bf.close()


@pytest.mark.smoke
class TestScalableBloomFilterLargeCmmap(GenericFilterTest):

    CAPACITY = 20000

    def setUp(self):
        super(TestScalableBloomFilterLargeCmmap, self).setUp()
        self.filter = ScalableBloomFilter(
            mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def tearDown(self):
        self.filter.close()


class TestScalableBloomfilterSmallCmmap(GenericFilterTest):

    CAPACITY = 500

    def setUp(self):
        super(TestScalableBloomfilterSmallCmmap, self).setUp()
        self.filter = ScalableBloomFilter(
            mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def tearDown(self):
        self.filter.close()


class TestScalableBloomFilterLargeSeekFile(GenericFilterTest):

    CAPACITY = 20000

    def setUp(self):
        super(TestScalableBloomFilterLargeSeekFile, self).setUp()
        self.filter = ScalableBloomFilter(
            mode=ScalableBloomFilter.LARGE_SET_GROWTH,
            filter_impl=WrappedFileSeekBloomFilter)

    def tearDown(self):
        self.filter.close()


@pytest.mark.smoke
class TestScalableBloomfilterSmallSeekFile(GenericFilterTest):

    CAPACITY = 500

    def setUp(self):
        super(TestScalableBloomfilterSmallSeekFile, self).setUp()
        self.filter = ScalableBloomFilter(
            mode=ScalableBloomFilter.LARGE_SET_GROWTH,
            filter_impl=WrappedFileSeekBloomFilter)

    def tearDown(self):
        self.filter.close()
