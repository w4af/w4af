"""
test_phishtank_xml_parsing.py

Copyright 2006 Andres Riancho

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
import os
import unittest
import lxml.etree as etree
import pytest

from w4af import ROOT_PATH

PHISHTANK_DB = os.path.join(ROOT_PATH, 'plugins', 'crawl', 'phishtank',
                            'index.xml')


class TestPhishTankParseMethods(unittest.TestCase):
    def test_target_parser(self):
        pytest.skip('This method is awful in terms of memory usage')

        with open(PHISHTANK_DB) as phishtank_db_fd:
            # pylint: disable=E0602
            pt_handler = PhishTankHandler([])
            parser = etree.HTMLParser(recover=True, target=pt_handler)
            etree.parse(phishtank_db_fd, parser)

    def test_iterparse(self):
        pytest.skip('This method is awful in terms of memory usage')

        with open(PHISHTANK_DB) as phishtank_db_fd:
            context = etree.iterparse(phishtank_db_fd, events=('end',), html=True)
            for action, elem in context:
                pass

    def test_iterparse_remove_unused(self):
        """
        https://stackoverflow.com/questions/12160418/why-is-lxml-etree-iterparse-eating-up-all-my-memory
        """
        pytest.skip('This method is awful in terms of memory usage, even'
                       ' with the calls to elem.clear() which I hoped would'
                       ' improve it. This solution also has the issue of'
                       ' being awfully slow.')

        def fast_iter(context, func, *args, **kwargs):
            """
            http://lxml.de/parsing.html#modifying-the-tree
            Based on Liza Daly's fast_iter
            http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
            See also http://effbot.org/zone/element-iterparse.htm
            """
            for event, elem in context:
                func(elem, *args, **kwargs)
                # It's safe to call clear() here because no descendants will be
                # accessed
                elem.clear()

                # Also eliminate now-empty references from the root node to elem
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

            del context

        with open(PHISHTANK_DB) as phishtank_db_fd:
            def process_element(elem):
                pass

            context = etree.iterparse(phishtank_db_fd, events=('end',),
                                    tag='entry', html=True)
            fast_iter(context, process_element)