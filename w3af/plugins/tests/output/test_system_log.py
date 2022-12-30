"""
test_csv_file.py

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
import csv
import json
import os
import pytest

from w4af.core.data.kb.vuln import Vuln
from w4af.core.data.dc.urlencoded_form import URLEncodedForm
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.url import URL
from w4af.plugins.tests.helper import PluginTest, PluginConfig
from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.data.fuzzer.mutants.querystring_mutant import QSMutant
from w4af.core.data.fuzzer.mutants.postdata_mutant import PostDataMutant
from w4af.core.data.request.fuzzable_request import FuzzableRequest


@pytest.mark.moth
class TestSystemLog(PluginTest):
    """Placeholder to keep the unittest coverage test from failing"""

    OUTPUT_FILE = 'output-system-log-unittest.log'

    target_url = get_moth_http('/audit/xss/simple_xss.py?text=1')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (
                    PluginConfig(
                        'xss',
                         ('checkStored', True, PluginConfig.BOOL),
                         ('numberOfChecks', 3, PluginConfig.INT)),
                ),
                'crawl': (
                    PluginConfig(
                        'web_spider',
                        ('only_forward', True, PluginConfig.BOOL)),
                ),
                'output': (
                    PluginConfig(
                        'system_log',
                        ('output_file', OUTPUT_FILE, PluginConfig.STR)),
                )
            },
        }
    }

    def tearDown(self):
        try:
            os.remove(self.OUTPUT_FILE)
        except:
            pass