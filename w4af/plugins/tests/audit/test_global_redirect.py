"""
test_global_redirect.py

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
import unittest
from unittest import TestCase

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse
from w4af.plugins.audit.global_redirect import global_redirect
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers


SCAN_CONFIG = {
    'cfg': {
        'target': None,
        'plugins': {
            'audit': (PluginConfig('global_redirect'),),
            'crawl': (
                PluginConfig(
                    'web_spider',
                    ('only_forward', True, PluginConfig.BOOL)),
            )
        }
    },
}


@pytest.mark.moth
class TestGlobalRedirect(PluginTest):

    target_url = get_moth_http('/audit/global_redirect/')

    def test_found_redirect(self):
        cfg = SCAN_CONFIG['cfg']
        cfg['target'] = self.target_url
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('global_redirect', 'global_redirect')

        self.assertAllVulnNamesEqual('Insecure redirection', vulns)

        # Verify the specifics about the vulnerabilities
        EXPECTED = [
            ('redirect-javascript.py', 'url'),
            ('redirect-meta.py', 'url'),
            ('redirect-302.py', 'url'),
            ('redirect-header-302.py', 'url'),
            ('redirect-302-filtered.py', 'url')
        ]

        self.assertExpectedVulnsFound(EXPECTED, vulns)


@pytest.mark.skip("Works locally, fails in a suite / CI")
class TestGlobalRedirectBasic(PluginTest):

    target_url = 'http://httpretty'

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   '<a href="/redir?target=">redirect</a>'),
                      MockResponse('http://httpretty/redir?target=',
                                   'No redirect'),
                      MockResponse('http://httpretty/redir?target=http://www.w4af.org/',
                                   status=302,
                                   headers={'Location': 'https://www.w4af.org/'},
                                   body='')]

    def test_original_response_has_no_redirect(self):
        cfg = SCAN_CONFIG['cfg']
        cfg['target'] = self.target_url

        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('global_redirect', 'global_redirect')
        expected = [('redir', 'target')]

        self.assertAllVulnNamesEqual('Insecure redirection', vulns)
        self.assertExpectedVulnsFound(expected, vulns)


@pytest.mark.skip("Works locally, fails in a suite / CI")
class TestGlobalRedirectBasicWithMetaRedir(PluginTest):

    target_url = 'http://httpretty'

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   '<a href="/redir?target=">redirect</a>'),
                      MockResponse('http://httpretty/redir?target=',
                                   '<meta http-equiv="refresh" content="0; url=">'),
                      MockResponse('http://httpretty/redir?target=http://www.w4af.org/',
                                   body='<meta http-equiv="refresh" content="0; url=http://www.w4af.org/">')]

    def test_original_response_has_meta_redirect(self):
        cfg = SCAN_CONFIG['cfg']
        cfg['target'] = self.target_url

        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('global_redirect', 'global_redirect')
        expected = [('redir', 'target')]

        self.assertAllVulnNamesEqual('Insecure redirection', vulns)
        self.assertExpectedVulnsFound(expected, vulns)


@pytest.mark.skip("Works locally, fails in a suite / CI")
class TestGlobalRedirectExtendedPayloadSet(PluginTest):

    target_url = 'http://httpretty'

    MOCK_RESPONSES = [MockResponse('http://httpretty/',
                                   '<a href="/redir?target=">redirect</a>'),
                      MockResponse('http://httpretty/redir?target=',
                                   status=302,
                                   headers={'Location': 'http://httpretty/default'},
                                   body=''),
                      MockResponse('http://httpretty/redir?target=//httpretty.w4af.org/',
                                   status=302,
                                   headers={'Location': 'httpretty.w4af.org'},
                                   body='')]

    def test_original_response_has_redirect(self):
        cfg = SCAN_CONFIG['cfg']
        cfg['target'] = self.target_url

        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('global_redirect', 'global_redirect')
        expected = [('redir', 'target')]

        self.assertAllVulnNamesEqual('Insecure redirection', vulns)
        self.assertExpectedVulnsFound(expected, vulns)


class TestGlobalRedirectUnitExtractScript(TestCase):
    def test_extract_script_code_simple(self):
        plugin = global_redirect()

        body = '<script>var x=1;var y=2;</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        code = plugin._extract_script_code(resp)
        code = [c for c in code]

        self.assertEqual(code, ['var x=1', 'var y=2'])

    def test_extract_script_code_new_line(self):
        plugin = global_redirect()

        body = '<script>var x=1;\nvar y=2;alert(1)</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        code = plugin._extract_script_code(resp)
        code = [c for c in code]

        self.assertEqual(code, ['var x=1', 'var y=2', 'alert(1)'])


class TestGlobalRedirectUnitJSRedirect(TestCase):
    def test_javascript_redirect_simple(self):
        plugin = global_redirect()

        body = '<script>window.location = "http://w4af.org/"</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._javascript_redirect(resp))

    def test_javascript_redirect_assign(self):
        plugin = global_redirect()

        body = '<script>window.location.assign("http://www.w4af.org")</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._javascript_redirect(resp))


class TestGlobalRedirectUnitResponseHasRedirect(TestCase):
    def test_response_has_redirect_headers(self):
        plugin = global_redirect()

        body = ''
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'), ('Location',  'http://w4af.org')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._response_has_redirect(resp))

    @unittest.skip('Mysterious failure')
    def test_response_has_redirect_meta(self):
        plugin = global_redirect()

        body = '<meta http-equiv="refresh" content="0; url=">'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._response_has_redirect(resp))

    def test_response_has_redirect_js_1(self):
        plugin = global_redirect()

        body = '<script>window.location.assign("http://www.w4af.org")</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._response_has_redirect(resp))

    def test_response_has_redirect_js_2(self):
        plugin = global_redirect()

        body = '<script>window.location.href = "http://www.w4af.org"</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertTrue(plugin._response_has_redirect(resp))

    def test_response_has_redirect_js_false(self):
        plugin = global_redirect()

        body = '<script>alert(window.location)</script>'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertFalse(plugin._response_has_redirect(resp))

    def test_response_has_redirect_headers_false(self):
        plugin = global_redirect()

        body = '<meta generator="">'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.assertFalse(plugin._response_has_redirect(resp))
