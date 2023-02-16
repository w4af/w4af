"""
ldapi.py

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


import w4af.core.data.constants.severity as severity
import w4af.core.controllers.output_manager as om

from w4af.core.controllers.plugins.audit_plugin import AuditPlugin
from w4af.core.data.quick_match.multi_in import MultiIn
from w4af.core.data.fuzzer.fuzzer import create_mutants
from w4af.core.data.kb.vuln import Vuln
from w4af.core.data.misc.encoding import smart_str_ignore


class ldapi(AuditPlugin):
    """
    Find LDAP injection bugs.
    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    LDAP_ERRORS = (
        # Not sure which lang or LDAP engine
        b'supplied argument is not a valid ldap',

        # Java
        b'javax.naming.NameNotFoundException',
        b'LDAPException',
        b'com.sun.jndi.ldap',

        # PHP
        b'Bad search filter',

        # http://support.microsoft.com/kb/218185
        b'Protocol error occurred',
        b'Size limit has exceeded',
        b'An inappropriate matching occurred',
        b'A constraint violation occurred',
        b'The syntax is invalid',
        b'Object does not exist',
        b'The alias is invalid',
        b'The distinguished name has an invalid syntax',
        b'The server does not handle directory requests',
        b'There was a naming violation',
        b'There was an object class violation',
        b'Results returned are too large',
        b'Unknown error occurred',
        b'Local error occurred',
        b'The search filter is incorrect',
        b'The search filter is invalid',
        b'The search filter cannot be recognized',

        # OpenLDAP
        b'Invalid DN syntax',
        b'No Such Object',

        # IPWorks LDAP
        # http://www.tisc-insight.com/newsletters/58.html
        b'IPWorksASP.LDAP',

        # https://entrack.enfoldsystems.com/browse/SERVERPUB-350
        b'Module Products.LDAPMultiPlugins'
    )

    _multi_in = MultiIn(LDAP_ERRORS)

    LDAPI_STRINGS = ["^(#$!@#$)(()))******", ]

    def audit(self, freq, orig_response, debugging_id):
        """
        Tests an URL for LDAP injection vulnerabilities.

        :param freq: A FuzzableRequest
        :param orig_response: The HTTP response associated with the fuzzable request
        :param debugging_id: A unique identifier for this call to audit()
        """
        mutants = create_mutants(freq, self.LDAPI_STRINGS,
                                 orig_resp=orig_response)

        self._send_mutants_in_threads(self._uri_opener.send_mutant,
                                      mutants,
                                      self._analyze_result,
                                      debugging_id=debugging_id)

    def _analyze_result(self, mutant, response):
        """
        Analyze results of the _send_mutant method.
        """
        #
        #   I will only report the vulnerability once.
        #
        if self._has_no_bug(mutant):

            ldap_error_list = self._find_ldap_error(response)
            for ldap_error_string in ldap_error_list:
                if ldap_error_string not in mutant.get_original_response_body():
                    
                    desc = 'LDAP injection was found at: %s' % mutant.found_at()
                    
                    v = Vuln.from_mutant('LDAP injection vulnerability', desc,
                                         severity.HIGH, response.id,
                                         self.get_name(), mutant)
                    
                    v.add_to_highlight(ldap_error_string)
                    
                    self.kb_append_uniq(self, 'ldapi', v)
                    break

    def _find_ldap_error(self, response):
        """
        This method searches for LDAP errors in html's.

        :param response: The HTTP response object
        :return: A list of errors found on the page
        """
        res = []
        for match_string in self._multi_in.query(smart_str_ignore(response.body)):
            msg = ('Found LDAP error string. The error returned by the web'
                   ' application is (only a fragment is shown): "%s". The error'
                   ' was found in response with ID %s')
            om.out.information(msg % (match_string, response.id))
            res.append(match_string)
        return res

    def get_plugin_deps(self):
        """
        :return: A list with the names of the plugins that should be run before the
        current one.
        """
        return ['grep.error_500']

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin will find LDAP injections by sending a specially crafted
        string to every parameter and analyzing the response for LDAP errors.
        """
