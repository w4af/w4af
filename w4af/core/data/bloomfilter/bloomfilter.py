# -*- encoding: utf-8 -*-
"""
bloomfilter.py

Copyright 2011 Andres Riancho

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
from bloom_filter2 import BloomFilter as WrappedBloomFilter

from w4af.core.data.bloomfilter.wrappers import GenericBloomFilter

class BloomFilter(GenericBloomFilter):
    def __init__(self, capacity, error_rate):
        """
        :param capacity: How many items you want to store, eg. 10000
        :param error_rate: The acceptable false positive rate, eg. 0.001
        """
        GenericBloomFilter.__init__(self, capacity, error_rate)

        temp_file = self.get_temp_file()
        self.bf = WrappedBloomFilter(max_elements=capacity, error_rate=error_rate, filename=(temp_file, -1))
