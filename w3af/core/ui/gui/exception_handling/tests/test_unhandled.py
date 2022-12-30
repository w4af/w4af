"""
test_unhandled.py

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
import pytest

from unittest.mock import MagicMock, Mock, patch

from w4af.core.ui.gui.exception_handling.unhandled import handle_crash, set_except_hook


class TestUnhandled(unittest.TestCase):

    def setUp(self):
        self.w4af_core = Mock()

    def test_set_except_hook(self):
        set_except_hook(self.w4af_core)
        self.assertTrue(True)

    def test_handle_exception(self):
        pytest.skip('For unknown reasons this test hangs by consuming tons of CPU and memory.')
    
        with patch('w4af.core.ui.gui.exception_handling.unhandled.sys') as mock_sys:
            handle_crash(self.w4af_core, KeyboardInterrupt, Mock(), Mock())
            mock_sys.exit.called_once_with(0)