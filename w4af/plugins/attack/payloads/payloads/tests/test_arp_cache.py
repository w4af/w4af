"""
test_arp_cache.py

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
@pytest.mark.smoke
class test_arp_cache(ApachePayloadTestHelper):

    # Not used because I want to be less specific in this case
    EXPECTED_RESULT = {'192.168.56.1': ('0a:00:27:00:00:00', 'eth1'), }

    def test_arp_cache(self):
        result = exec_payload(self.shell, 'arp_cache', use_api=True)
        for ip_address, (mac, iface) in result.items():
            self.assertEqual(ip_address.count('.'), 3)
            self.assertEqual(mac.count(':'), 5)
            self.assertTrue(iface.startswith('eth'))
