"""
test_zero_webappsecurity_com.py

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

from w4af.tests.vuln_sites.utils.scan_vulnerable_site import TestScanVulnerableSite
from w4af.plugins.tests.helper import PluginTest


@pytest.mark.external_group1
@pytest.mark.slow
class TestZeroWebAppSecurityCom(TestScanVulnerableSite, PluginTest):

    target_url = 'http://zero.webappsecurity.com'
    EXPECTED_VULNS = {('CSRF vulnerability', '/faq.html', None),
                      ('Interesting META tag', '/faq.html', None),
                      ('DAV incorrect configuration', '/gJEVl', None),
                      ('Interesting META tag', '/', None),
                      ('Interesting META tag', '/index.html', None),
                      ('Identified cookie', '/bank/account-summary.html', None),
                      ('Interesting META tag', '/help.html', None),
                      ('DAV methods enabled', '/', None),
                      ('Cookie', '/bank/account-summary.html', None),
                      ('Server header', None, None),
                      ('DAV incorrect configuration', '/resources/css/ndAXD', None),
                      ('AJAX code', '/resources/js/jquery-1.6.4.min.js', None),
                      ('Strange HTTP response code', '/search.html', None),
                      ('DAV incorrect configuration', '/resources/img/pkuJO', None),
                      ('Interesting META tag', '/feedback.html', None),
                      ('DAV incorrect configuration', '/resources/js/soyxK', None),
                      ('Identified cookie', '/bank/transfer-funds.html', None),
                      ('Interesting META tag', '/search.html', None),
                      ('CSRF vulnerability', '/login.html', None),
                      ('Interesting META tag', '/forgot-password.html', None),
                      ('Interesting META tag', '/login.html', None),
                      ('Interesting META tag', '/online-banking.html', None),
                      ('Click-Jacking vulnerability', None, None),
                      ('Strange HTTP response code', '/sendFeedback.html', None)}
