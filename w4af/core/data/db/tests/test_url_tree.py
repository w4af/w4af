# -*- coding: UTF-8 -*-
"""
Copyright 2018 Andres Riancho

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

from w4af.core.data.db.url_tree import URLTree, URLNode, url_tree_factory
from w4af.core.data.parsers.doc.url import URL


class TestURLTree(unittest.TestCase):
    def test_empty(self):
        tree = URLTree()
        self.assertEqual(tree.tree, {})

    def test_root(self):
        tree = URLTree()

        url = URL('http://w4af.net/')
        tree.add_url(url)

        expected = {URLNode('http://w4af.net', 1): {}}
        self.assertEqual(tree.tree, expected)

    def test_two_independent_paths(self):
        tree = URLTree()

        url_1 = URL('http://w4af.net/foo/')
        url_2 = URL('http://w4af.net/bar/')
        tree.add_url(url_1)
        tree.add_url(url_2)

        expected = {URLNode("http://w4af.net", 0): {URLNode("foo", 1): {},
                                                    URLNode("bar", 1): {}}}
        self.assertEqual(tree.tree, expected)

    def test_two_nested_paths(self):
        tree = URLTree()

        url_1 = URL('http://w4af.net/foo/bar/')
        url_2 = URL('http://w4af.net/spam/eggs/')
        tree.add_url(url_1)
        tree.add_url(url_2)

        expected = {URLNode("http://w4af.net", 0):
                        {URLNode("foo", 0): {URLNode("bar", 1): {}},
                         URLNode("spam", 0): {URLNode("eggs", 1): {}}}}

        self.assertEqual(tree.tree, expected)

    def test_nested_paths_and_files(self):
        tree = URLTree()

        url_1 = URL('http://w4af.net/foo/bar/')
        url_2 = URL('http://w4af.net/spam/eggs/123.txt')
        tree.add_url(url_1)
        tree.add_url(url_2)

        expected = {URLNode("http://w4af.net", 0):
                        {URLNode("foo", 0): {URLNode("bar", 1): {}},
                         URLNode("spam", 0): {URLNode("eggs", 0): {URLNode("123.txt", 1): {}}}}}

        self.assertEqual(tree.tree, expected)

