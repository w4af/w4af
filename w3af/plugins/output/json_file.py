"""
json_file.py

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
import os
import base64
import json
import time

import w4af.core.data.kb.knowledge_base as kb
import w4af.core.data.kb.config as cf
import w4af.core.controllers.output_manager as om

from w4af.core.controllers.plugins.output_plugin import OutputPlugin
from w4af.core.controllers.misc import get_w4af_version
from w4af.core.data.options.opt_factory import opt_factory
from w4af.core.data.options.option_types import OUTPUT_FILE
from w4af.core.data.options.option_list import OptionList

TIME_FORMAT = '%a %b %d %H:%M:%S %Y'


class json_file(OutputPlugin):
    """
    Export identified vulnerabilities to a JSON file.

    :author: jose nazario (jose@monkey.org)
    """

    def __init__(self):
        OutputPlugin.__init__(self)
        self.output_file = '~/output-w4af.json'
        self._timestamp = str(int(time.time()))
        self._long_timestamp = str(time.strftime(TIME_FORMAT, time.localtime()))

        # Set defaults for scan metadata
        self._plugins_dict = {}
        self._options_dict = {}        
        self._enabled_plugins = {}        
    
    def do_nothing(self, *args, **kwargs):
        pass

    debug = log_http = vulnerability = do_nothing
    information = error = console = do_nothing

    def end(self):
        self.flush()

    def log_enabled_plugins(self, plugins_dict, options_dict):
        """
        This method is called from the output manager object. This method
        should take an action for the enabled plugins and their configuration.
        Usually, write the info to a file or print it somewhere.

        :param plugins_dict: A dict with all the plugin types and the
                                enabled plugins for that type of plugin.
        :param options_dict: A dict with the options for every plugin.
        """
        # TODO: Improve so it contains the plugin configuration too
        for plugin_type, enabled in plugins_dict.items():
            self._enabled_plugins[plugin_type] = enabled        

    def flush(self):
        """
        Exports the vulnerabilities and information to the user configured
        file.
        """
        self.output_file = os.path.expanduser(self.output_file)

        try:
            with open(self.output_file, 'w') as output_handler:

                target_urls = [t.url_string for t in cf.cf.get('targets')]

                target_domain = 'unknown'
                if cf.cf.get('target_domains'):
                    target_domain = cf.cf.get('target_domains')[0]

                enabled_plugins = self._enabled_plugins

                def _get_desc(x):
                    try:
                        return x._desc
                    except AttributeError:
                        return None

                def _encode_post_data(info):
                    data = info.get_mutant().get_data()
                    if data is None:
                        return None
                    return base64.b64encode(data).decode('utf-8')

                findings = [_f for _f in [_get_desc(x) for x in kb.kb.get_all_findings_iter()] if _f]
                known_urls = [str(x) for x in kb.kb.get_all_known_urls()]

                items = []
                for info in kb.kb.get_all_findings_iter():
                    try:
                        item = {"Severity": info.get_severity(),
                                "Name": info.get_name(),
                                "HTTP method": info.get_method(),
                                "URL": str(info.get_url()),
                                "Vulnerable parameter": info.get_token_name(),
                                "POST data": _encode_post_data(info),
                                "Vulnerability IDs": info.get_id(),
                                "CWE IDs": getattr(info, "cwe_ids", []),
                                "WASC IDs": getattr(info, "wasc_ids", []),
                                "Tags": getattr(info, "tags", []),
                                "VulnDB ID": info.get_vulndb_id(),
                                "Description": info.get_desc()}
                        items.append(item)
                    except Exception as e:
                        msg = ('An exception was raised while trying to write the '
                            ' vulnerabilities to the output file. Exception: "%s"')
                        om.out.error(msg % e)
                        return

                res = {'w4af-version': get_w4af_version.get_w4af_version(),
                    'scan-info': {'target_urls': target_urls,
                                    'target_domain': target_domain,
                                    'enabled_plugins': enabled_plugins,
                                    'findings': findings,
                                    'known_urls': known_urls},
                    'start': self._timestamp,
                    'start-long': self._long_timestamp,
                    'items': items}

                json.dump(res, output_handler, indent=4)

        except IOError as ioe:
            msg = 'Failed to open the output file for writing: "%s"'
            om.out.error(msg % ioe)
            return

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin exports all identified vulnerabilities to a JSON file.
        
        Each report contains information about the scan
          * w4af-version
          * Start time
          * Known URLs
          * Enabled plugins
          * Target URLs
          * Target domain
          * Findings
        
        Each finding in the sequence contains the following fields:
          * Severity
          * Name
          * HTTP method
          * URL
          * Vulnerable parameter
          * Base64 encoded POST-data
          * Unique vulnerability ID
          * CWE IDs
          * WASC IDs
          * Tags
          * VulnDB ID
          * Severity
          * Description
            
        The JSON plugin should be used for quick and easy integrations with w4af,
        external tools which require more details, such as the HTTP request and
        response associated with each vulnerability, should use the xml_file
        output plugin.
        
        One configurable parameter exists:
            - output_file
        """

    def set_options(self, option_list):
        """
        Sets the Options given on the OptionList to self. The options are the
        result of a user entering some data on a window that was constructed
        using the XML Options that was retrieved from the plugin using
        get_options()
        :return: No value is returned.
        """
        self.output_file = option_list['output_file'].get_value()

    def get_options(self):
        """
        :return: A list of option objects for this plugin.
        """
        ol = OptionList()

        d = 'The name of the output file where the vulnerabilities are be saved'
        o = opt_factory('output_file', self.output_file, d, OUTPUT_FILE)
        ol.add(o)

        return ol    
