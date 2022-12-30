"""
test_kb_add.py

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

from w4af.core.ui.console.console_ui import ConsoleUI
from w4af.core.ui.console.tests.helper import ConsoleTestHelper


@pytest.mark.smoke
class TestKBAdd(ConsoleTestHelper):
    """
    Basic test for the console UI.
    """
    def test_kb_add(self):
        commands_to_run = ['kb',
                                'add dav',
                                    'set url http://target.com/',
                                    'back',
                                'list vulns',
                                'back',
                            'exit',]

        self.console = ConsoleUI(commands=commands_to_run, do_upd=False)
        self.console.sh()

        expected = ('w4af>>> ',
                    'w4af/kb>>> ',
                    'w4af/kb/config:dav>>> ',
                    'Stored "DAV Misconfiguration" in the knowledge base.',
                    '| DAV              | This vulnerability was added to the knowledge')
        
        assert_result, msg = self.startswith_expected_in_output(expected)
        self.assertTrue(assert_result, msg)
    
    def test_kb_add_with_errors(self):
        commands_to_run = ['kb',
                                'add',
                                'add foobar',
                                'add foo bar',
                                'back',
                            'exit',]

        self.console = ConsoleUI(commands=commands_to_run, do_upd=False)
        self.console.sh()

        expected = ('w4af>>> ',
                    'w4af/kb>>> ',
                    'Parameter "type" is missing,',
                    'Type foobar is unknown',
                    'Only one parameter is accepted,')
        
        assert_result, msg = self.startswith_expected_in_output(expected)
        self.assertTrue(assert_result, msg)

    def test_kb_add_back_without_config(self):
        commands_to_run = ['kb',
                                'add',
                                'add os_commanding',
                                'back',
                            'exit',]

        self.console = ConsoleUI(commands=commands_to_run, do_upd=False)
        self.console.sh()

        expected = ('w4af>>> ',
                    'w4af/kb>>> ',
                    'This vulnerability requires data to be configured.',
                    )
        
        assert_result, msg = self.startswith_expected_in_output(expected)
        self.assertTrue(assert_result, msg)