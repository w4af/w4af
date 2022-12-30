"""
test_phishing_vector.py

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

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.moth
class TestPhishingVector(PluginTest):

    target_url = get_moth_http('/audit/phishing_vector/')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('phishing_vector'),),
                'crawl': (
                    PluginConfig(
                        'web_spider',
                        ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        },
    }

    def test_found_phishing_vector(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('phishing_vector', 'phishing_vector')

        # Verify the specifics about the vulnerabilities
        EXPECTED = [
            ('http_blacklist_phishing.py', 'url'),
            ('iframe_phishing.py', 'url'),
            ('frame_phishing.py', 'url'),
        ]

        self.assertAllVulnNamesEqual('Phishing vector', vulns)
        self.assertExpectedVulnsFound(EXPECTED, vulns)
