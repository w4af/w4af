"""
php_sca.py

Copyright 2011 Andres Riancho

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
import tempfile

import w4af.core.data.constants.severity as severity
import w4af.core.data.kb.knowledge_base as kb
import w4af.core.controllers.output_manager as om

from w4af.core.data.dc.generic.nr_kv_container import NonRepeatKeyValueContainer
from w4af.core.data.kb.vuln import Vuln
from w4af.core.controllers.sca.sca import PhpSCA
from w4af.core.ui.console.tables import table
from w4af.plugins.attack.payloads.base_payload import Payload


class php_sca(Payload):

    KB_DATA = {
        'XSS': {'kb_key': ('xss', 'xss'),
                'severity': severity.MEDIUM,
                'name': 'Cross site scripting vulnerability'},

        'OS_COMMANDING': {'kb_key': ('os_commanding', 'os_commanding'),
                          'severity': severity.HIGH,
                          'name': 'OS commanding vulnerability'},

        'FILE_INCLUDE': {'kb_key': ('lfi', 'lfi'),
                         'severity': severity.MEDIUM,
                         'name': 'Local file inclusion vulnerability'},
    }

    def api_read(self, localtmpdir=None):
        """
        :param localtmpdir: Local temporary directory where to save
                            the remote code.
        """
        def write_vuln_to_kb(vulnty, url, funcs):
            vulndata = php_sca.KB_DATA[vulnty]
            for f in funcs:
                vuln_sev = vulndata['severity']
                desc = name = vulndata['name']
                
                v = Vuln(name, desc, vuln_sev, 1, 'PHP Static Code Analyzer')
                v.set_uri(url)
                dc = NonRepeatKeyValueContainer()
                dc.update({(f.vulnsources[0], 0): None})

                args = list(vulndata['kb_key']) + [v]

                # TODO: Extract the method from the PHP code
                #     $_GET == GET
                #     $_POST == POST
                #     $_REQUEST == GET
                v.set_method('GET')

                # TODO: Extract all the other variables that are
                # present in the PHP file using the SCA
                v.set_dc(dc)

                #
                # TODO: This needs to be checked! OS Commanding specific
                #       attributes.
                v['os'] = 'unix'
                v['separator'] = ''

                kb.kb.append(*args)

        if not localtmpdir:
            localtmpdir = tempfile.mkdtemp()

        res = {}
        files = self.exec_payload('get_source_code', args=(localtmpdir,))

        # Error handling
        if isinstance(files, str):
            om.out.console(files)
            return {}

        # Was able to download files
        for url, file in files.items():
            try:
                sca = PhpSCA(file=file[1])
                vulns = sca.get_vulns()
            except Exception as e:
                msg = 'The PHP SCA failed with an unhandled exception: "%s".'
                om.out.console(msg % e)
                return {}

            for vulnty, funcs in vulns.items():
                # Write to KB
                write_vuln_to_kb(vulnty, url, funcs)
                # Fill res dict
                res.setdefault(vulnty, []).extend(
                    [{'loc': url, 'lineno': fc.lineno, 'funcname': fc.name,
                      'vulnsrc': str(fc.vulnsources[0])} for fc in funcs])

        return res

    def run_read(self):

        api_res = self.api_read()
        if not api_res:
            return 'No vulnerability was found.'

        rows = [['Vuln Type', 'Remote Location', 'Vuln Param', 'Lineno'], []]
        for vulnty, files in api_res.items():
            for f in files:
                rows.append(
                    [vulnty, str(f['loc']), f['vulnsrc'], str(f['lineno'])])

        restable = table(rows)
        restable.draw(100)
        return rows
