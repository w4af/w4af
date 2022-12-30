"""
test_web_diff.py

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
import os

import pytest
from unittest.mock import patch, call

from w4af import ROOT_PATH
from w4af.core.data.parsers.doc.url import URL
from w4af.plugins.tests.helper import PluginTest, PluginConfig
from w4af.core.controllers.ci.w4af_moth import get_w4af_moth_http


@pytest.mark.w4af_moth
class TestWebDiff(PluginTest):

    target_url = get_w4af_moth_http('/w4af/crawl/web_diff/')
    local_dir = os.path.join(ROOT_PATH, 'plugins', 'tests', 'crawl', 'web_diff')

    _run_configs = {
        'basic': {
            'target': target_url,
            'plugins': {
                'crawl': (
                    PluginConfig('web_diff',
                                 ('content', True, PluginConfig.BOOL),
                                 ('local_dir', local_dir, PluginConfig.STR),
                                 ('remote_url_path',
                                  URL(target_url), PluginConfig.URL),
                                 (
                                     'banned_ext', 'php,foo,bar', PluginConfig.LIST)),
                )
            }
        },
    }

    @pytest.mark.ci_fails
    def test_compare(self):
        cfg = self._run_configs['basic']

        with patch('w4af.plugins.crawl.web_diff.om.out') as om_mock:
            self._scan(cfg['target'], cfg['plugins'])

            EXPECTED_CALLS = [
                call.information('The following files exist in the local'
                                 ' directory and in the remote server:'),
                call.information(
                    '- %s/456.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information(
                    '- %s/exclude.php' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information(
                    '- %s/123.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information(
                    '- %s/index.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information('The following files exist in the local'
                                 ' directory and in the remote server and'
                                 ' their contents match:'),
                call.information(
                    '- %s/123.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information(
                    '- %s/index.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information("The following files exist in the local"
                                 " directory and in the remote server but"
                                 " their contents don't match:"),
                call.information(
                    '- %s/456.html' % get_w4af_moth_http('/w4af/crawl/web_diff')),
                call.information('Match files: 4 of 4'),
                call.information('Match contents: 2 of 3')
            ]

            for ecall in EXPECTED_CALLS:
                self.assertIn(ecall, om_mock.mock_calls)