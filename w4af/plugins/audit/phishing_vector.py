"""
phishing_vector.py

Copyright 2006 Andres Riancho

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


import w4af.core.controllers.output_manager as om
import w4af.core.data.constants.severity as severity
import w4af.core.data.parsers.parser_cache as parser_cache

from w4af.core.data.fuzzer.fuzzer import create_mutants
from w4af.core.controllers.plugins.audit_plugin import AuditPlugin
from w4af.core.data.kb.vuln import Vuln


class phishing_vector(AuditPlugin):
    """
    Find phishing vectors.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    TAGS = ('iframe', 'frame')

    # I test this with different URL handlers because the developer may have
    # blacklisted http:// and https:// but missed ftp://.
    #
    # I also use hTtp instead of http because I want to evade some (stupid)
    # case sensitive filters
    TEST_URLS = ('hTtp://w4af.net/',
                 'htTps://w4af.net/',
                 'fTp://w4af.net/',
                 '//w4af.net')

    def audit(self, freq, orig_response, debugging_id):
        """
        Find those phishing vectors!

        :param freq: A FuzzableRequest
        :param orig_response: The HTTP response associated with the fuzzable request
        :param debugging_id: A unique identifier for this call to audit()
        """
        mutants = create_mutants(freq, self.TEST_URLS)

        self._send_mutants_in_threads(self._uri_opener.send_mutant,
                                      mutants,
                                      self._analyze_result,
                                      debugging_id=debugging_id)

        om.out.debug('Finished audit.phishing_vector (did=%s)' % debugging_id)

    def _contains_payload(self, response):
        """
        get_tags_by_filter is CPU-intensive (but cached whenever possible), and
        we want to prevent calls to it, so we first check if the HTTP response
        body contains the payloads we sent.

        :param response: The HTTP response body
        :return: True if the response body contains at least one of the payloads
        """
        body = response.body
        body = body.lower()

        for test_url in self.TEST_URLS:
            if test_url.lower() in body:
                return True

        return False

    def _analyze_result(self, mutant, response):
        """
        Analyze results of the _send_mutant method.
        """
        if not response.is_text_or_html():
            return

        if self._has_bug(mutant):
            return

        # Performance improvement to prevent calling the CPU-expensive
        # get_tags_by_filter
        if not self._contains_payload(response):
            return

        for tag in parser_cache.dpc.get_tags_by_filter(response, self.TAGS):
            # pylint: disable=E1101
            src_attr = tag.attrib.get('src', None)
            # pylint: enable=E1101

            if src_attr is None:
                continue

            for url in self.TEST_URLS:
                if not src_attr.startswith(url):
                    continue

                # Vuln vuln!
                desc = 'A phishing vector was found at: %s'
                desc %= mutant.found_at()

                v = Vuln.from_mutant('Phishing vector', desc, severity.LOW,
                                     response.id, self.get_name(), mutant)

                v.add_to_highlight(src_attr)
                self.kb_append_uniq(self, 'phishing_vector', v)
                break

        msg = ('Performed HTTP response analysis at audit.phishing_vector URL %s,'
               ' HTTP response ID %s.')
        args = (response.get_uri(), response.id)
        om.out.debug(msg % args)

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugins identifies phishing vectors in web applications, a bug of
        this type is found if the victim requests the URL
        "http://site.tld/asd.asp?info=http://attacker.tld" and the HTTP response
        contains:

            ...
            <iframe src="http://attacker.tld">
            ...
        """
