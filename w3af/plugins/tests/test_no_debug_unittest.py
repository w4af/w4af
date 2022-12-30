"""
test_no_debug_unittest.py

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
import unittest
import os
import re

from w4af import ROOT_PATH


def recursive_listdir(path):
    basedir = path

    for item in os.listdir(path):
        
        item_full_path = os.path.join(basedir, item)
        
        if os.path.isfile(item_full_path):
            yield item_full_path
        else:
            for item in recursive_listdir(item_full_path):
                yield item
        
class TestNoDebugUnittest(unittest.TestCase):
    
    def test_no_kb_access_from_plugin(self):
        
        debug_scan = re.compile('self._scan(.*?, *debug)')
        
        for unittest_file in recursive_listdir(os.path.join(ROOT_PATH, 
                                                            'plugins',
                                                            'tests')):

            if not unittest_file.endswith('.py') or\
            not 'test_' in unittest_file:
                continue
            
            with open(unittest_file) as fh:
                test_code = fh.read()
            
            if debug_scan.search(test_code):
                msg = '%s unittest has debugging enabled in the scan method.'
                self.assertTrue(False, msg % unittest_file)
                
                