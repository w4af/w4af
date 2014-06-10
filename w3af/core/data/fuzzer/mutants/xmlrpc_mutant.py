"""
XmlRpcMutant.py

Copyright 2009 Andres Riancho

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
from w3af.core.data.fuzzer.mutants.postdata_mutant import PostDataMutant
from w3af.core.data.request.xmlrpc_request import XMLRPCRequest


class XmlRpcMutant(PostDataMutant):
    """
    This class is an XMLRPC mutant.
    """
    def get_mutant_type(self):
        return 'XMLRPC data'

    def found_at(self):
        """
        I had to implement this again here instead of just inheriting from
        PostDataMutant because of the duplicated parameter name support which
        I added to the framework.

        :return: A string representing WHAT was fuzzed.
        """
        res = ''
        res += '"' + self.get_url() + '", using HTTP method '
        res += self.get_method() + '. The sent XML-RPC was: "'
        res += str(self.get_dc())
        res += '"'
        return res

    @staticmethod
    def create_mutants(freq, mutant_str_list, fuzzable_param_list,
                       append, fuzzer_config, data_container=None):
        """
        This is a very important method which is called in order to create
        mutants. Usually called from fuzzer.py module.
        """
        if not isinstance(freq, XMLRPCRequest):
            return []

        return XmlRpcMutant._create_mutants_worker(freq, XmlRpcMutant,
                                                   mutant_str_list,
                                                   fuzzable_param_list,
                                                   append, fuzzer_config)