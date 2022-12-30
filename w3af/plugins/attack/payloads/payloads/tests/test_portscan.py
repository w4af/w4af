"""
test_portscan.py

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

from w4af.plugins.attack.payloads.payloads.tests.payload_test_helper_exec import PayloadTestHelperExec
from w4af.plugins.attack.payloads.payload_handler import exec_payload


class test_portscan(PayloadTestHelperExec):

    RESULT_80 = {'localhost': ['80']}
    RESULT_23 = {'localhost': []}

    @pytest.mark.ci_fails
    @pytest.mark.phpmoth
    def test_portscan(self):
        result = exec_payload(self.shell, 'portscan',
                              args=('localhost', '80'),
                              use_api=True)
        self.assertEqual(self.RESULT_80, result)

        result = exec_payload(self.shell, 'portscan',
                              args=('localhost', '23'),
                              use_api=True)
        self.assertEqual(self.RESULT_23, result)