"""
test_list_processes.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from nose.plugins.attrib import attr

from w3af.plugins.attack.payloads.payloads.tests.payload_test_helper import PayloadTestHelper
from w3af.plugins.attack.payloads.payload_handler import exec_payload


@attr('slow')
@attr('ci_fails')
class test_list_processes(PayloadTestHelper):

    EXPECTED_RESULT = set([
        '/usr/bin/python2.7 manage.py trunserver 0.0.0.0:8000',
        '/usr/bin/python /usr/bin/supervisord'
    ])

    def test_list_processes(self):
        result = exec_payload(
            self.shell, 'list_processes', args=(2000,), use_api=True)

        cmds = []
        for _, pid_data in result.items():
            cmds.append(pid_data['cmd'])

        for expected in self.EXPECTED_RESULT:
            self.assertIn(expected, cmds)
