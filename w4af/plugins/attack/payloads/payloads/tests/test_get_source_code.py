"""
test_get_source_code.py

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
import tempfile
import shutil

import pytest
from w4af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w4af.plugins.attack.payloads.payload_handler import exec_payload
from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http


class test_get_source_code(ApachePayloadTestHelper):

    EXPECTED_RESULT = {"/w4af/audit/local_file_read/local_file_read.php":
                       (
                       '/var/www/moth/w4af/audit/local_file_read/local_file_read.php',
                       'tmp__random__/var/www/moth/w4af/audit/local_file_read/local_file_read.php')
                       }

    CONTENT = "echo file_get_contents( $_REQUEST['file'] );"

    @pytest.mark.ci_fails
    @pytest.mark.w4af_moth
    def test_get_source_code(self):
        temp_dir = tempfile.mkdtemp()
        result = exec_payload(self.shell, 'get_source_code', args=(temp_dir,),
                              use_api=True)

        self.assertEqual(len(list(self.EXPECTED_RESULT.keys())), 1)

        expected_url = get_w4af_moth_http(list(self.EXPECTED_RESULT.keys())[0])
        downloaded_url = list(result.items())[0][0].url_string
        self.assertEqual(expected_url, downloaded_url)

        downloaded_file_path = list(result.items())[0][1][1]
        with open(downloaded_file_path) as download_fh:
            downloaded_file_content = download_fh.read()
        self.assertTrue(self.CONTENT in downloaded_file_content)

        shutil.rmtree(temp_dir)