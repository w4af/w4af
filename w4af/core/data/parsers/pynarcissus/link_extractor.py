"""
link_extractor.py

Copyright 2014 Andres Riancho

This file is part of w4af, https://w4af.net/ .

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
from w4af.core.data.parsers.pynarcissus.string_extractor import StringExtractor
from w4af.core.data.parsers.utils.url_regex import URL_RE, RELATIVE_URL_RE
from w4af.core.data.parsers.doc.url import URL


class JSLinkExtractor(StringExtractor):
    """
    :see: Docstring in StringExtractor
    """
    def get_links(self):
        return self.extract_full_urls()

    def extract_full_urls(self):
        urls = set()
        merged_strings = ' \n'.join(self.get_strings())

        for x in URL_RE.findall(merged_strings):
            try:
                urls.add(URL(x[0]))
            except ValueError:
                pass

        return urls
