"""
test_vulners_db.py

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
import pytest
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse


class TestVulnersDB(PluginTest):

    target_url = 'http://httpretty'
    allow_net_connect = True

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   body='',
                                   method='GET',
                                   status=200,
                                   headers={'content-length': '0',
                                            'server': 'Microsoft-IIS/7.5',
                                            'x-aspnet-version': '2.0.50727',
                                            'x-powered-by': 'ASP.NET',
                                            'microsoftsharepointteamservices': '14.0.0.4762'}),
                      ]

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('vulners_db'),),
                'crawl': (
                    PluginConfig('web_spider',
                                 ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        }
    }

    # There are a couple of things that are broken about this test:
    # 1. The vulners API requires an API key, which isn't supplied by the test
    #    setup.
    # 2. HTTPretty is not well maintained, and hits a bug when real requests are
    #    made to HTTPS servers while HTTPretty is active:
    #    https://github.com/gabrielfalcao/HTTPretty/issues/65
    #    This can be mitigated if keep-alive is disabled for the real requests:
    #    headers=Headers(init_val=[("Connection", "close")])
    #    but our plugin only controls one of the real fetches - the live API calls
    #    are made by the Vulners package, and we can't meddle with the fetching in there.
    #    Per the comment in #65, the 'responses' python package doesn't have this issue,
    #    but the responses package can only mock high-level requests made with the 'requests'
    #    package.
    #    Using @mock.patch to stub the _send_request method of VulnersApi would potentially
    #    be an option, but it gets pretty prickly because vulners is using some code generation
    #    to generate its low-level API fetch interface.
    # Another approach would be also to mock the requests to the vulners API. This would
    # make our test here more of a unit than an integration test, but that is for sure better
    # than nothing
    @pytest.mark.skip("Not working because of httpretty bug")
    def test_vulns_detected(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('vulners_db', 'HTML')

        self.assertEqual(len(vulns), 5, vulns)

        expected_names = {'CVE-2010-2730',
                          'CVE-2010-1256',
                          'CVE-2010-3972',
                          'CVE-2012-2531',
                          'CVE-2010-1899'}

        names = {i.get_name() for i in vulns}

        self.assertEqual(names, expected_names)

        vuln = [i for i in vulns if i.get_name() == 'CVE-2012-2531'][0]

        self.assertEqual(vuln.get_name(), 'CVE-2012-2531')
        self.assertEqual(vuln.get_url().url_string, 'http://httpretty/')

        expected_desc = ('Vulners plugin detected software with known vulnerabilities.'
                         ' The identified vulnerability is "CVE-2012-2531".\n'
                         '\n'
                         ' The first ten URLs where vulnerable software was detected are:\n'
                         ' - http://httpretty/\n')
        self.assertEqual(vuln.get_desc(with_id=False), expected_desc)

