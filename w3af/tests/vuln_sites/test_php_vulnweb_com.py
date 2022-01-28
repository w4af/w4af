"""
test_php_vulnweb_com.py

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


class TestScanPHPVulnwebCom(TestScanVulnerableSite, PluginTest):

    target_url = 'http://testphp.vulnweb.com/'
    EXPECTED_VULNS = {('Uncommon query string parameter', '/showimage.php', None),
                      ('SQL injection', '/listproducts.php', 'cat'),
                      ('Browser plugin content', '/signup.php', None),
                      ('Strange HTTP response code', '/kjxcn', None),
                      ('Browser plugin content', '/cart.php', None),
                      ('AJAX code', '/AJAX/index.php', None),
                      ('Cross site scripting vulnerability', '/guestbook.php', 'name'),
                      ('Uncommon query string parameter', '/hpp/params.php', None),
                      ('Path disclosure vulnerability', '/artists.php', None),
                      ('Browser plugin content', '/artists.php', None),
                      ('Directory indexing', '/Flash/', None),
                      ('Browser plugin content', '/index.php', None),
                      ('SQL injection', '/product.php', 'pic'),
                      ('Browser plugin content', '/login.php', None),
                      ('Path disclosure vulnerability', '/search.php', None),
                      ('SQL injection', '/userinfo.php', 'pass'),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'uemail'),
                      ('SQL injection', '/search.php', 'test'),
                      ('Path disclosure vulnerability', '/guestbook.php', None),
                      ('Browser plugin content', '/listproducts.php', None),
                      ('Server header', None, None),
                      ('Path disclosure vulnerability', '/listproducts.php', None),
                      ('Powered-by header', None, None),
                      ('Auto-completable form', '/signup.php', None),
                      ('SQL injection', '/secured/newuser.php', 'uuname'),
                      ('Browser plugin content', '/', None),
                      ('Cross site scripting vulnerability', '/guestbook.php', 'text'),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'uphone'),
                      ('Insecure redirection', '/redir.php', 'r'),
                      ('Path disclosure vulnerability', '/hpp/params.php', None),
                      ('Browser plugin content', '/disclaimer.php', None),
                      ('Unhandled error in web application', '/redir.php', None),
                      ('Auto-completable form', '/login.php', None),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'uuname'),
                      ('Cross site scripting vulnerability', '/showimage.php', 'file'),
                      ('Allowed HTTP methods', '/', None),
                      ('Blank http response body', '/secured/', None),
                      ('Cross site scripting vulnerability', '/search.php', 'searchFor'),
                      ('Parameter modifies response headers', '/redir.php', 'r'),
                      ('SQL injection', '/userinfo.php', 'uname'),
                      ('SQL injection', '/listproducts.php', 'artist'),
                      ('Cross site scripting vulnerability', '/hpp/params.php', 'p'),
                      ('Strange HTTP response code', '/redir.php', None),
                      ('Path disclosure vulnerability', '/redir.php', None),
                      ('Browser plugin content', '/search.php', None),
                      ('Cross site scripting vulnerability', '/hpp/params.php', 'pp'),
                      ('Remote file inclusion', '/showimage.php', 'file'),
                      ('Browser plugin content', '/guestbook.php', None),
                      ('Cross site scripting vulnerability', '/hpp/', 'pp'),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'uaddress'),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'urname'),
                      ('Click-Jacking vulnerability', None, None),
                      ('AJAX code', '/AJAX/', None),
                      ('Browser plugin content', '/categories.php', None),
                      ('Browser plugin content', '/product.php', None),
                      ('SQL injection', '/artists.php', 'artist'),
                      ('Path disclosure vulnerability', '/product.php', None),
                      ('Potential buffer overflow vulnerability', '/showimage.php', 'size'),
                      ('Strange HTTP Reason message', '/redir.php', None),
                      ('Cross site scripting vulnerability', '/secured/newuser.php', 'ucc'),
                      ('Local file inclusion vulnerability', '/showimage.php', 'file')}
