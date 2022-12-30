"""
test_list_processes.py

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

from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload


@pytest.mark.w4af_moth
@pytest.mark.slow
@pytest.mark.ci_fails
class test_list_processes(ApachePayloadTestHelper):

    EXPECTED_RESULT = set([
        '/bin/sh /usr/bin/mysqld_safe',
        '/usr/bin/python3 /usr/local/bin/supervisord -n'
    ])

    def test_list_processes(self):
        result = exec_payload(
            self.shell, 'list_processes', args=(2000,), use_api=True)

        cmds = []
        for _, pid_data in result.items():
            cmds.append(pid_data['cmd'])

        for expected in self.EXPECTED_RESULT:
            self.assertIn(expected, cmds)
