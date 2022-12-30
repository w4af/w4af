"""
test_crawl_infrastructure.py

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
import time

import pytest

import w4af.core.data.kb.config as cf

from w4af.plugins.tests.helper import PluginTest, PluginConfig
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.ci.moth import get_moth_http


class TestTimeLimit(PluginTest):

    target_url = get_moth_http()

    _run_configs = {
        'basic': {
            'target': target_url,
            'plugins': {
                'crawl': (
                    PluginConfig('web_spider',),
                )
            }
        },
    }

    @pytest.mark.ci_fails
    @pytest.mark.moth
    def test_spider_with_time_limit(self):
        #
        #    First scan
        #
        cf.cf.save('max_discovery_time', 0.05)
        cfg = self._run_configs['basic']
        
        start_time = time.time()
        
        self._scan(self.target_url, cfg['plugins'])

        end_time = time.time()
        first_scan_time = end_time - start_time

        len_first_urls = len(self.kb.get_all_known_urls())
        self.assertGreater(len_first_urls, 40)
        self.assertLess(first_scan_time, 30)
        
        # Cleanup
        self.w4afcore.quit()
        self.kb.cleanup()
        self.w4afcore = w4afCore()
        
        #
        #    Second scan
        #
        cf.cf.save('max_discovery_time', 1)
        cfg = self._run_configs['basic']
        
        start_time = time.time()
        
        self._scan(self.target_url, cfg['plugins'])
        
        end_time = time.time()
        second_scan_time = end_time - start_time

        len_second_urls = len(self.kb.get_all_known_urls())
        self.assertGreater(len_second_urls, 100)
        self.assertGreater(len_second_urls, len_first_urls)
        self.assertLess(second_scan_time, 60)
        
        self.assertGreater(second_scan_time, first_scan_time)
