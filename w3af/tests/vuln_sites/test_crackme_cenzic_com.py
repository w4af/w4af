"""
test_crackme_cenzic_com.py

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


class TestScanCrackmeCenzicCom(TestScanVulnerableSite, PluginTest):

    target_url = 'http://crackme.cenzic.com'
    EXPECTED_VULNS = {('Interesting HTML comment', '/Kelev/view/credit.php', None),
                      ('HTML comment contains HTML code', '/Kelev/view/loanrequest.php', None),
                      ('Interesting HTML comment', '/Kelev/loans/studentloan.php', None),
                      ('Interesting HTML comment', '/Kelev/view/terms.php', None),
                      ('Interesting HTML comment', '/Kelev/view/privacy.php', None),
                      ('Strange HTTP response code', '/WGVbF', None),
                      ('Interesting HTML comment', '/Kelev/view/kelev2.php', None),
                      ('Auto-completable form', '/Kelev/php/loginbm.php', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'drpLoanType'),
                      ('Server header', None, None),
                      ('Interesting HTML comment', '/Kelev/register/register.php', None),
                      ('Interesting HTML comment', '/Kelev/view/trade.php', None),
                      ('Allowed HTTP methods', '/', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtDOB'),
                      ('Interesting HTML comment', '/Kelev/view/billsonline.php', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtAddress'),
                      ('Interesting HTML comment', '/Kelev/loans/homeloan.php', None),
                      ('Interesting HTML comment', '/Kelev/php/login.php', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtTelephoneNo'),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtCity'),
                      ('Cross site scripting vulnerability', '/Kelev/view/updateloanrequest.php', 'txtFirstName'),
                      ('Powered-by header', None, None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'drpState'),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtLastName'),
                      ('Interesting HTML comment', '/Kelev/view/feedback.php', None),
                      ('SQL injection', '/Kelev/view/updateloanrequest.php', 'txtAnnualIncome'),
                      ('Auto-completable form', '/Kelev/php/login.php', None),
                      ('Interesting HTML comment', '/Kelev/view/loanrequest.php', None),
                      ('Interesting HTML comment', '/Kelev/loans/carloanmain.php', None),
                      ('Interesting HTML comment', '/Kelev/view/netbanking.php', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtSocialScurityNo'),
                      ('Auto-completable form', '/Kelev/register/register.php', None),
                      ('Strange HTTP Reason message', '/Kelev/view/updateloanrequest.php', None),
                      ('Interesting HTML comment', '/Kelev/php/loginbm.php', None),
                      ('Interesting HTML comment', '/Kelev/view/rate.php', None),
                      ('Click-Jacking vulnerability', None, None),
                      ('Cross site tracing vulnerability', '/', None),
                      ('Unidentified vulnerability', '/Kelev/view/updateloanrequest.php', 'txtEmail'),
                      ('Interesting HTML comment', '/Kelev/view/home.php', None)}
