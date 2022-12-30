"""
test_helper_requirements_txt.py

Copyright 2013 Andres Riancho

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

from unittest.mock import patch

from w4af.core.controllers.dependency_check.helper_requirements_txt import generate_requirements_txt
from w4af.core.controllers.dependency_check.pip_dependency import PIPDependency 


class TestGenerateTXT(unittest.TestCase):
    
    MOCK_TARGET = 'w4af.core.controllers.ci.only_ci_decorator.is_running_on_ci'
    
    @patch(MOCK_TARGET, return_value=True)
    def test_generate_requirements_txt_empty(self, ci_mock):
        requirements_file = generate_requirements_txt([])
        
        with open(requirements_file) as reqs:
            count = len(reqs.read())
        self.assertEqual(0, count)
        os.unlink(requirements_file)

    @patch(MOCK_TARGET, return_value=True)
    def test_generate_requirements_txt(self, ci_mock):
        EXPECTED = 'a==1.2.3\nc==3.2.1\n'
        requirements_file = generate_requirements_txt([PIPDependency('a', 'a', '1.2.3'),
                                                       PIPDependency('b', 'c', '3.2.1'),])
        
        with open(requirements_file) as text:
            received = text.read()
        self.assertEqual(EXPECTED, received)
        os.unlink(requirements_file)
        