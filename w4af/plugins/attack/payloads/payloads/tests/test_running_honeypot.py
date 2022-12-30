"""
test_running_honeypot.py

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
class test_running_honeypot(ApachePayloadTestHelper):

    EXPECTED_RESULT = {'is_a_honeypot': False, 'running_honeypot': False}

    def test_running_honeypot(self):
        result = exec_payload(self.shell, 'running_honeypot', use_api=True)
        self.assertEqual(self.EXPECTED_RESULT, result)

    @pytest.mark.ci_fails
    def test_a_positive_test(self):
        pytest.skip('FIXME: I need a positive test.')