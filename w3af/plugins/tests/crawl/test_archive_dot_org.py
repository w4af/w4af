"""
test_archive_dot_org.py

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

from w4af.core.controllers.exceptions import RunOnce
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.url.extended_urllib import ExtendedUrllib
from w4af.plugins.crawl.archive_dot_org import archive_dot_org
from w4af.plugins.tests.helper import PluginTest, PluginConfig


@pytest.mark.skip("Archive.org has changed - better to use the API to make this plugin work")
class TestArchiveDotOrg(PluginTest):

    archive_url = 'http://w4af.org/'

    _run_config = {
        'target': None,
        'plugins': {'crawl': (PluginConfig('archive_dot_org',),)}
    }

    @pytest.mark.ci_fails
    def test_found_urls(self):
        self._scan(self.archive_url, self._run_config['plugins'])
        urls = self.kb.get_all_known_urls()

        EXPECTED_URLS = ('download', 'take-a-tour', 'community', 'blog',
                         'howtos', 'project-history')

        expected_set = set((self.archive_url + end) for end in EXPECTED_URLS)
        urls_as_strings = set([u.url_string for u in urls])

        msg = 'Got the following URLs %s and expected %s.'
        msg = msg % (urls_as_strings, expected_set)

        self.assertTrue(urls_as_strings.issuperset(expected_set), msg)
        self.assertGreater(len(urls), 50)

    def test_raise_on_local_domain(self):
        url = URL('http://moth/')
        fr = FuzzableRequest(url, method='GET')
        ado = archive_dot_org()
        self.assertRaises(RunOnce, ado.discover_wrapper, fr, None)

    def test_raise_on_domain_not_in_archive(self):
        url = URL('http://www.w4af-scanner.org/')
        fr = FuzzableRequest(url, method='GET')

        ado = archive_dot_org()
        uri_opener = ExtendedUrllib()
        ado.set_url_opener(uri_opener)

        self.assertRaises(RunOnce, ado.discover_wrapper, fr, None)
