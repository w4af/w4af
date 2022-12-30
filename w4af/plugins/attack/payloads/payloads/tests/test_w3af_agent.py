"""
test_w4af_agent.py

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

from w4af.core.controllers.misc.get_local_ip import get_local_ip

from w4af.plugins.attack.payloads.payloads.tests.payload_test_helper_exec import PayloadTestHelperExec
from w4af.plugins.attack.payloads.payload_handler import exec_payload
from w4af.plugins.tests.helper import onlyroot


class test_w4af_agent(PayloadTestHelperExec):

    @pytest.mark.ci_fails
    @pytest.mark.phpmoth
    def test_w4af_agent(self):
        result = exec_payload(self.shell, 'w4af_agent', args=(get_local_ip(),),
                              use_api=True)
        self.assertEqual('Successfully started the w4afAgent.', result)
