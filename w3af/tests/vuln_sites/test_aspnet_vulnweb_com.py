"""
test_aspnet_vulnweb_com.py

Copyright 2014 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from w3af.tests.vuln_sites.utils.scan_vulnerable_site import TestScanVulnerableSite
from w3af.plugins.tests.helper import PluginTest


class TestScanASPNETVulnwebCom(TestScanVulnerableSite, PluginTest):

    target_url = 'http://testaspnet.vulnweb.com/'
    EXPECTED_VULNS = {('.NET ViewState encryption is disabled', '/', None),
                      ('Uncommon query string parameter', '/ReadNews.aspx', None),
                      ('Interesting META tag', '/Default.aspx', None),
                      ('Uncommon query string parameter', '/Comments.aspx', None),
                      ('.NET ViewState encryption is disabled', '/about.aspx', None),
                      ('Interesting META tag', '/', None),
                      ('Blind SQL injection vulnerability', '/login.aspx', 'tbUsername'),
                      ('Interesting META tag', '/ReadNews.aspx', None),
                      ('CSRF vulnerability', '/ReadNews.aspx', None),
                      ('Blind SQL injection vulnerability', '/ReadNews.aspx', 'id'),
                      ('CSRF vulnerability', '/Comments.aspx', None),
                      ('Auto-completable form', '/Signup.aspx', None),
                      ('Server header', None, None),
                      ('Phishing vector', '/ReadNews.aspx', 'NewsAd'),
                      ('Auto-completable form', '/login.aspx', None),
                      ('Interesting META tag', '/Comments.aspx', None),
                      ('ReDoS vulnerability', '/ReadNews.aspx', 'id'),
                      ('.NET ViewState encryption is disabled', '/default.aspx', None),
                      ('.NET ViewState encryption is disabled', '/login.aspx', None),
                      ('Cross site scripting vulnerability', '/ReadNews.aspx', 'NewsAd'),
                      ('Powered-by header', None, None),
                      ('.NET ViewState encryption is disabled', '/Comments.aspx', None),
                      ('Interesting META tag', '/Signup.aspx', None),
                      ('Content feed resource', '/rssFeed.aspx', None),
                      ('Blind SQL injection vulnerability', '/Comments.aspx', 'tbComment'),
                      ('.NET ViewState encryption is disabled', '/Default.aspx', None),
                      ('Blank http response body', '/ReadNews.aspx', None),
                      ('Unhandled error in web application', '/ReadNews.aspx', None),
                      ('Cross site scripting vulnerability', '/Comments.aspx', 'tbComment'),
                      ('Interesting META tag', '/about.aspx', None),
                      ('Blind SQL injection vulnerability', '/Comments.aspx', 'id'),
                      ('Interesting META tag', '/default.aspx', None),
                      ('OS commanding vulnerability', '/ReadNews.aspx', 'id'),
                      ('.NET ViewState encryption is disabled', '/ReadNews.aspx', None),
                      ('Click-Jacking vulnerability', None, None),
                      ('Allowed HTTP methods', '/', None),
                      ('Interesting META tag', '/login.aspx', None),
                      ('Blank http response body', '/Comments.aspx', None),
                      ('.NET ViewState encryption is disabled', '/Signup.aspx', None)}
