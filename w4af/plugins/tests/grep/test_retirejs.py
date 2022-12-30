"""
test_retirejs.py

Copyright 2018 Andres Riancho

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
import unittest
import requests
import httpretty

from w4af import ROOT_PATH
from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse
from w4af.plugins.grep.retirejs import retirejs

import pytest

RETIRE_DB_URL = 'https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository.json'
RETIRE_DB = requests.get(RETIRE_DB_URL).content

@pytest.mark.internet
class TestRetireJSNotAnalyzeHTMLContentType(PluginTest):

    target_url = 'http://httpretty'

    # This is a vulnerable version of JQuery
    JQUERY_VULN = os.path.join(ROOT_PATH, 'plugins', 'tests', 'grep', 'retirejs', 'jquery.js')

    INDEX = '<html><script src="/js/jquery.js"></script></html>'

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   body=INDEX,
                                   method='GET',
                                   status=200),
                      MockResponse('http://httpretty/js/jquery.js',
                                   body=open(JQUERY_VULN).read(),
                                   method='GET',
                                   status=200,
                                   content_type='text/html'),
                      ]

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('retirejs'),),
                'crawl': (
                    PluginConfig('web_spider',
                                 ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        }
    }

    def test_is_vulnerable_not_detected(self):
        httpretty.register_uri('GET', RETIRE_DB_URL, body=RETIRE_DB)
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('retirejs', 'js')

        self.assertEqual(len(vulns), 0, vulns)


EXPECTED_VULN_DESC = '''\
A JavaScript library with known vulnerabilities was identified at http://httpretty/js/jquery.js. The library was identified as "jquery" version 1.11.0 and has these known vulnerabilities:

 - 3rd party CORS request may execute
 - parseHTML() executes scripts in event handlers
 - jQuery before 3.4.0, as used in Drupal, Backdrop CMS, and other products, mishandles jQuery.extend(true, {}, ...) because of Object.prototype pollution
 - Regex in its jQuery.htmlPrefilter sometimes may introduce XSS
 - Regex in its jQuery.htmlPrefilter sometimes may introduce XSS

Consider updating to the latest stable release of the affected library.'''


@pytest.mark.internet
class TestRetireJS(PluginTest):

    target_url = 'http://httpretty'

    # This is a vulnerable version of JQuery
    JQUERY_VULN = os.path.join(ROOT_PATH, 'plugins', 'tests', 'grep', 'retirejs', 'jquery.js')

    INDEX = '<html><script src="/js/jquery.js"></script></html>'

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   body=INDEX,
                                   method='GET',
                                   status=200),
                      MockResponse('http://httpretty/js/jquery.js',
                                   body=open(JQUERY_VULN).read(),
                                   method='GET',
                                   status=200,
                                   content_type='application/javascript'),
                      ]

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('retirejs'),),
                'crawl': (
                    PluginConfig('web_spider',
                                 ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        }
    }

    def test_is_vulnerable_detected(self):
        httpretty.register_uri('GET', RETIRE_DB_URL, body=RETIRE_DB)
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('retirejs', 'js')

        self.assertEqual(len(vulns), 1, vulns)

        vuln = vulns[0]

        self.assertEqual(vuln.get_name(), 'Vulnerable JavaScript library in use')
        self.assertEqual(vuln.get_url().url_string, 'http://httpretty/js/jquery.js')
        self.assertEqual(vuln.get_desc(with_id=False), EXPECTED_VULN_DESC)


@pytest.mark.internet
class TestRetireJSClass(unittest.TestCase):
    def setUp(self):
        create_temp_dir()

    def test_version_check(self):
        rjs = retirejs()
        self.assertTrue(rjs._get_is_valid_retire_version())

    def test_retire_smoke_test(self):
        rjs = retirejs()
        self.assertTrue(rjs._retire_smoke_test())
