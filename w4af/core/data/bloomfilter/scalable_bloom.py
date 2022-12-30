# -*- encoding: utf-8 -*-
"""
scalable_bloom.py

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
from w4af.core.data.bloomfilter.bloomfilter import BloomFilter

def make_hashable(key):
    if hasattr(key, '__divmod__'):
        return key
    if isinstance(key, (str, bytes, list, tuple)) and not key:
        return key
    if isinstance(key, tuple):
        return "-".join([ str(x) for x in key ])
    if isinstance(key, (str, bytes)):
        return key
    if not hasattr(key, '__getitem__'):
        return str(key)
    if hasattr(key[0], '__divmod__'):
        int_list = key
    if isinstance(key[0], str):
        return key
    return "-".join([ str(x) for x in key ])

class ScalableBloomFilter(object):
    SMALL_SET_GROWTH = 2  # slower, but takes up less memory
    LARGE_SET_GROWTH = 4  # faster, but takes up more memory faster

    def __init__(self, initial_capacity=15000, error_rate=0.000001,
                 mode=SMALL_SET_GROWTH, filter_impl=BloomFilter):
        """Implements a space-efficient probabilistic data structure that
        grows as more items are added while maintaining a steady false
        positive rate

        initial_capacity
            the initial capacity of the filter
        error_rate
            the error_rate of the filter returning false positives. This
            determines the filters capacity. Going over capacity greatly
            increases the chance of false positives.
        mode
            can be either ScalableBloomFilter.SMALL_SET_GROWTH or
            ScalableBloomFilter.LARGE_SET_GROWTH. SMALL_SET_GROWTH is slower
            but uses less memory. LARGE_SET_GROWTH is faster but consumes
            memory faster.
        """
        if not error_rate or error_rate < 0:
            raise ValueError("Error_Rate must be a decimal less than 0.")

        self.filter_impl = filter_impl
        self.scale = mode
        self.ratio = 0.9
        self.initial_capacity = initial_capacity
        self.error_rate = error_rate
        self.filters = []

    def __contains__(self, key):
        """Tests a key's membership in this bloom filter.

        >>> b = ScalableBloomFilter(initial_capacity=100, error_rate=0.001, \
                                    mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        >>> b.add("hello")
        True
        >>> "hello" in b
        True

        """
        hashable_key = make_hashable(key)
        for f in reversed(self.filters):
            if hashable_key in f:
                return True
        return False

    def add(self, key):
        """
        Adds a key to this bloom filter.

        If the key already exists in this filter it will return False (because
        it failed to add it to the filter). Otherwise True.

        >>> b = ScalableBloomFilter(initial_capacity=100, error_rate=0.001, \
                                    mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        >>> b.add("hello")
        True
        >>> b.add("hello")
        False

        """
        hashable_key = make_hashable(key)
        if hashable_key in self:
            return False

        _filter = self.filters[-1] if self.filters else None
        if _filter is None or len(_filter) >= _filter.capacity:
            num_filters = len(self.filters)

            new_capacity = self.initial_capacity * (self.scale ** num_filters)
            new_error_rate = self.error_rate * (self.ratio ** num_filters)

            _filter = self.filter_impl(capacity=new_capacity,
                                       error_rate=new_error_rate)

            self.filters.append(_filter)
        _filter.add(hashable_key)
        return True

    @property
    def capacity(self):
        """Returns the total capacity for all filters in this SBF"""
        return sum([f.capacity for f in self.filters])

    @property
    def count(self):
        return len(self)

    def __len__(self):
        """Returns the total number of elements stored in this SBF"""
        return sum([len(f) for f in self.filters])

    def close(self):
        if hasattr(self.filter_impl, 'close'):
            for filt in self.filters:
                filt.close()
