"""
test_cpu_info.py

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
import re
import pytest

from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload


@pytest.mark.w4af_moth
@pytest.mark.smoke
class test_cpu_info(ApachePayloadTestHelper):

    def parse_cpu_info(self, cpu_info):
        processor = re.search('(?<=model name\t: )(.*)', cpu_info)
        if processor:
            processor_string = processor.group(1)
            splitted = processor_string.split(' ')
            splitted = [i for i in splitted if i != '']
            processor_string = ' '.join(splitted)
            return processor_string
        else:
            return ''

    def read_cpu_info(self):
        with open("/proc/cpuinfo") as info:
            cpu_info = info.read()
            cores = re.search('(?<=cpu cores\t: )(.*)', cpu_info).group(1)
            processor = self.parse_cpu_info(cpu_info)
            return { 'cpu_cores': cores, 'cpu_info': processor }

    @pytest.mark.ci_fails
    def test_cpu_info(self):
        result = exec_payload(self.shell, 'cpu_info', use_api=True)
        self.assertEqual(self.read_cpu_info(), result)