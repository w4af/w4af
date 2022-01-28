"""
test_asp_vulnweb_com.py

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


class TestScanASPVulnwebCom(TestScanVulnerableSite, PluginTest):

    target_url = 'http://testasp.vulnweb.com/'
    EXPECTED_VULNS = {('CSRF vulnerability', '/showthread.asp', None),
                      ('SQL injection', '/Register.asp', 'tfUName'),
                      ('Path disclosure vulnerability', '/Search.asp', None),
                      ('Click-Jacking vulnerability', None, None),
                      ('CSRF vulnerability', '/Search.asp', None),
                      ('Local file inclusion vulnerability', '/Templatize.asp', 'item'),
                      ('Unhandled error in web application', '/Search.asp', None),
                      ('SQL injection', '/Login.asp', 'tfUName'),
                      ('Strange HTTP Reason message', '/showforum.asp', None),
                      ('Unhandled error in web application', '/Templatize.asp', None),
                      ('SQL injection', '/Register.asp', 'tfRName'),
                      ('SQL injection', '/showforum.asp', 'id'),
                      ('CSRF vulnerability', '/Login.asp', None),
                      ('Server header', None, None),
                      ('SQL injection', '/Register.asp', 'tfUPass'),
                      ('Cross site scripting vulnerability', '/Search.asp', 'tfSearch'),
                      ('CSRF vulnerability', '/Register.asp', None),
                      ('SQL injection', '/showthread.asp', 'id'),
                      ('Cross site scripting vulnerability', '/Login.asp', 'RetURL'),
                      ('Unhandled error in web application', '/showthread.asp', None),
                      ('Unhandled error in web application', '/Register.asp', None),
                      ('Powered-by header', None, None),
                      ('Insecure redirection', '/Login.asp', 'RetURL'),
                      ('SQL injection', '/Register.asp', 'tfEmail'),
                      ('Unhandled error in web application', '/showforum.asp', None),
                      ('Descriptive error page', '/Templatize.asp', None),
                      ('Auto-completable form', '/Register.asp', None),
                      ('Uncommon query string parameter', '/Logout.asp', None),
                      ('CSRF vulnerability', '/Templatize.asp', None),
                      ('CSRF vulnerability', '/showforum.asp', None),
                      ('SQL injection', '/Login.asp', 'tfUPass'),
                      ('Unidentified vulnerability', '/Register.asp', 'RetURL'),
                      ('SQL injection', '/Search.asp', 'tfSearch'),
                      ('Auto-completable form', '/Login.asp', None),
                      ('Allowed HTTP methods', '/', None)}
