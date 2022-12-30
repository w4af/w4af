"""
test_ssh_version.py

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

from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload


class test_ssh_version(ApachePayloadTestHelper):

    # Please note that this only works IF the remote end allows us to use
    # php wrappers and read the binary file with base64
    EXPECTED_RESULT = {'ssh_version': 'OpenSSH_5.9p1 Debian-5ubuntu1'}

    @pytest.mark.w4af_moth
    @unittest.skip("Binary base64 PHP requires not working, and not clear SSH binary contains version info")
    def test_ssh_version(self):
        result = exec_payload(self.shell, 'ssh_version', use_api=True)
        self.assertEqual(self.EXPECTED_RESULT, result)
