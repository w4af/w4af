"""
test_gcc_version.py

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
from w4af.plugins.attack.payloads.payloads.gcc_version import gcc_version

from unittest.mock import MagicMock

@pytest.mark.w4af_moth
class test_gcc_version(ApachePayloadTestHelper):

    PARSE_TESTS = [
        [
            'Linux version 4.19.0-14-amd64 (debian-kernel@lists.debian.org) (gcc version 8.3.0 (Debian 8.3.0-6)) #1 SMP Debian 4.19.171-2 (2021-01-30)',
            '8.3.0 (Debian 8.3.0-6)'
        ],
        [
            'Linux version 5.10.0-13-amd64 (debian-kernel@lists.debian.org) (gcc-10 (Debian 10.2.1-6) 10.2.1 20210110, GNU ld (GNU Binutils for Debian) 2.35.2) #1 SMP Debian 5.10.106-1 (2022-03-17)',
            'gcc-10 (Debian 10.2.1-6) 10.2.1 20210110, GNU ld (GNU Binutils for Debian)'
        ],
        [
            'Linux version 5.15.0-1020-azure (buildd@lcy02-amd64-081) (gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0, GNU ld (GNU Binutils for Ubuntu) 2.34) #25~20.04.1-Ubuntu SMP',
            'gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0, GNU ld (GNU Binutils for Ubuntu)'
        ]
    ]

    def test_version_parse(self):
        gcc = gcc_version(MagicMock())
        for example in self.PARSE_TESTS:
            result = gcc.parse_gcc_version(example[0])
            self.assertEqual(result, example[1])

    @pytest.mark.ci_fails
    def test_gcc_version(self):
        result = exec_payload(self.shell, 'gcc_version', use_api=True)
        self.assertTrue(result['gcc_version'].startswith("gcc"), result)