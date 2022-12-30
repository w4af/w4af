"""
test_phishtank.py

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
import csv
import pytest

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.plugins.tests.helper import PluginTest
from w4af.plugins.crawl.phishtank import phishtank
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.constants.severity import MEDIUM
from w4af.core.data.misc.file_utils import days_since_file_update
from w4af.core.data.fuzzer.utils import rand_alnum


@pytest.mark.moth
class TestPhishtank(PluginTest):

    safe_url = get_moth_http()
    phish_detail = 'http://www.phishtank.com/phish_detail.php?phish_id='

    def test_phishtank_no_match(self):
        phishtank_inst = self.w4afcore.plugins.get_plugin_inst('crawl',
                                                               'phishtank')
        
        debug_id = rand_alnum()
        phishtank_inst.crawl(FuzzableRequest(URL(self.safe_url)), debug_id)
        vulns = self.kb.get('phishtank', 'phishtank')

        self.assertEqual(len(vulns), 0, vulns)

    def get_vulnerable_url(self):
        with open(phishtank.PHISHTANK_DB) as phish_fh:
            pt_csv_reader = csv.reader(phish_fh, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            for phishing_url, phishtank_detail_url in pt_csv_reader:
                return phishing_url

    def get_last_vulnerable_url(self):
        with open(phishtank.PHISHTANK_DB) as phish_fh:
            pt_csv_reader = csv.reader(phish_fh, delimiter=' ',
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)

            for phishing_url, phishtank_detail_url in pt_csv_reader:
                pass

        return phishing_url

    def test_total_urls(self):
        with open(phishtank.PHISHTANK_DB) as phish_fh:
            total_lines = len(phish_fh.read().split('\n'))
        self.assertGreater(total_lines, 5000)

    def test_phishtank_match_url(self):
        phishtank_inst = self.w4afcore.plugins.get_plugin_inst('crawl',
                                                               'phishtank')
        
        debug_id = rand_alnum()
        vuln_url = URL(self.get_vulnerable_url())
        phishtank_inst.crawl(FuzzableRequest(vuln_url), debug_id)

        vulns = self.kb.get('phishtank', 'phishtank')

        self.assertEqual(len(vulns), 1, vulns)
        vuln = vulns[0]

        self.assertEqual(vuln.get_name(), 'Phishing scam')
        self.assertEqual(vuln.get_severity(), MEDIUM)
        self.assertEqual(vuln.get_url().get_domain(), vuln_url.get_domain())

    def test_phishtank_match_last_url(self):
        phishtank_inst = self.w4afcore.plugins.get_plugin_inst('crawl',
                                                               'phishtank')

        debug_id = rand_alnum()
        vuln_url = URL(self.get_last_vulnerable_url())
        phishtank_inst.crawl(FuzzableRequest(vuln_url), debug_id)

        vulns = self.kb.get('phishtank', 'phishtank')

        self.assertEqual(len(vulns), 1, vulns)
        vuln = vulns[0]

        self.assertEqual(vuln.get_name(), 'Phishing scam')
        self.assertEqual(vuln.get_severity(), MEDIUM)
        self.assertEqual(vuln.get_url().get_domain(), vuln_url.get_domain())

    def test_too_old_db(self):
        is_older = days_since_file_update(phishtank.PHISHTANK_DB, 30)

        msg = 'The phishtank database is too old, in order to update it'\
              ' please follow these steps:\n'\
              'w4af/plugins/crawl/phishtank/update.py\n'\
              'git commit -m "Updating phishtank database." w4af/plugins/crawl/phishtank/index.csv\n'\
              'git push\n'
        self.assertFalse(is_older, msg)