"""
test_dependency_check.py

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

from unittest.mock import patch

from ..dependency_check import dependency_check
from ..platforms.base_platform import CORE
from ..platforms.default import DefaultPlatform
from ..platforms.ubuntu1204 import Ubuntu1204

class TestDependencyCheck(unittest.TestCase):

    DEPE_MODULE = 'w4af.core.controllers.dependency_check.dependency_check'
    CURR_PLATFORM = '%s.get_current_platform' % DEPE_MODULE

    def test_works_at_this_workstation(self):
        """
        Test that the dependency check works well @ this system
        """
        must_exit = dependency_check(dependency_set=CORE, exit_on_failure=False, skip_external_commands=True)
        self.assertFalse(must_exit)

    def test_default_platform_core_all_deps(self):
        """
        Test that the dependency check works for core + default platform when
        the dependencies are met.
        """
        with patch(self.CURR_PLATFORM) as mock_curr_plat:
            mock_curr_plat.return_value = DefaultPlatform()
            must_exit = dependency_check(dependency_set=CORE,
                                         exit_on_failure=False,
                                         skip_external_commands=True)
            self.assertFalse(must_exit)

    def test_ubuntu1204_core(self):
        """
        Test that the dependency check works for core + ubuntu1204
        """
        with patch(self.CURR_PLATFORM) as mock_curr_plat:
            mock_curr_plat.return_value = Ubuntu1204()
            must_exit = dependency_check(dependency_set=CORE,
                                         exit_on_failure=False,
                                         skip_external_commands=True)
            self.assertFalse(must_exit)
