"""
apache_payload_test_helper.py

Copyright 2022 Arthur Taylor

This file is part of w4af, http://w4af.net/ .

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
import w4af.core.data.kb.config as cf

from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http
from w4af.plugins.attack.payloads.payloads.tests.payload_test_helper import PayloadTestHelper
from w4af.plugins.tests.helper import PluginTest, PluginConfig


class ApachePayloadTestHelper(PayloadTestHelper):

    target_url = get_w4af_moth_http('/w4af/audit/local_file_read/local_file_read.php?file=section.txt')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('lfi'),),
            }
        }
    }
