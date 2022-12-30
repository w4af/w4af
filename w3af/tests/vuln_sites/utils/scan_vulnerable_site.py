"""
test_scan_vulnerable_site.py

Copyright 2014 Andres Riancho

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

from w4af.plugins.tests.helper import PluginConfig


@pytest.mark.functional
@pytest.mark.internet
@pytest.mark.ci_fails
class TestScanVulnerableSite(object):

    target_url = None

    _run_configs = {
        'cfg': {
            'plugins': {
                'crawl': (PluginConfig('web_spider',),),
                'audit': (PluginConfig('all'),),
                'grep': (PluginConfig('all'),),
            }
        }
    }

    EXPECTED_URLS = {}

    EXPECTED_VULNS = {()}

    def test_scan_vulnerable_site(self):
        if self.target_url is None:
            return

        cfg = self._run_configs['cfg']
        self._scan(self.target_url, cfg['plugins'])

        self.assertMostExpectedVulnsFound(self.EXPECTED_VULNS)