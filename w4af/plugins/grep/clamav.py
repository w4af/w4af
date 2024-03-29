"""
clamav.py

Copyright 2013 Andres Riancho

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
import threading
import pyclamd

from collections import namedtuple

from pyclamd import ConnectionError

import w4af.core.controllers.output_manager as om

from w4af.core.controllers.plugins.grep_plugin import GrepPlugin
from w4af.core.data.kb.info import Info
from w4af.core.data.options.opt_factory import opt_factory
from w4af.core.data.options.option_list import OptionList
from w4af.core.data.options.option_types import STRING

class ClamdConnection:
    def __init__(self, socket_name):
        self.socket_name = socket_name

    def __enter__(self):
        self.socket = pyclamd.ClamdUnixSocket(filename=self.socket_name)
        return self.socket

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.socket.shutdown()
        except ConnectionError:
            self.socket._close_socket()

class clamav(GrepPlugin):
    """
    Uses ClamAV to identify malware on your site.

    :author: Andres Riancho (andres.riancho@gmail.com)
    :sponsor: Andri Herumurti (http://scoresecure.com/)
    """

    METHODS = ('GET',)
    HTTP_CODES = (200,)
    
    def __init__(self):
        GrepPlugin.__init__(self)
        
        self._properly_configured = None
        self._config_check_lock = threading.RLock()
        
        # User configured settings
        # Default for ubuntu installation
        self._clamd_socket = '/var/run/clamav/clamd.ctl'

    def grep(self, request, response):
        """
        Plugin entry point, send HTTP response bodies to ClamAV in an async
        way in order to avoid any delays in our process.
        
        Keep in mind that I need to wait for all answers from clamd in end()
        before finishing the plugin and that (if possible) I shouldn't send
        the same stream twice.

        When sending an HTTP response body to ClamAV, I'll try to send it
        without any decoding applied to it, just like it came from the wire.

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        """
        if not self._is_properly_configured():
            return
        
        if request.get_method() not in self.METHODS:
            return

        if response.get_code() not in self.HTTP_CODES:
            return
        
        args = (request, response)
        self.worker_pool.apply_async(self._scan_http_response, args=args,
                                     callback=self._report_result)

    def _is_properly_configured(self):
        """
        :return: True if the plugin can connect to the ClamAV daemon.
        """
        with self._config_check_lock:
            if self._properly_configured is not None:
                # Return the cached response
                return self._properly_configured
            
            if self._connection_test():
                msg = 'Using %s for scanning HTTP response bodies.'
                om.out.information(msg % self._get_clamd_version())
                self._properly_configured = True
                
            else:
                msg = ('The ClamAV plugin failed to connect to clamd using'
                       ' the provided unix socket: "%s". Please verify your'
                       ' configuration and try again.')
                om.out.error(msg % self._clamd_socket)
                self._properly_configured = False
            
            return self._properly_configured

    def _connection_test(self):
        """
        :return: True if it was possible to connect to the configured socket
        """
        try:
            with ClamdConnection(self._clamd_socket) as cd:
                return cd.ping() is True
        except:
            return False

    def _get_clamd_version(self):
        """
        :return: A string which contains the ClamAV version.
        """
        with ClamdConnection(self._clamd_socket) as cd:
            return cd.version()
    
    def _scan_http_response(self, request, response):
        """
        Scans an HTTP response body for malware and stores any findings in
        the knowledge base.
        
        :param request: The HTTP request
        :param response: The HTTP response
        :return: None
        """
        body = str(response.get_body())

        try:
            with ClamdConnection(self._clamd_socket) as cd:
                result_dict = cd.scan_stream(body)
        except Exception as e:
            msg = ('The ClamAV plugin failed to connect to clamd using'
                   ' the provided unix socket: "%s". Please verify your'
                   ' configuration and try again. The exception was: "%s".')
            om.out.error(msg % (self._clamd_socket, e))
            self._properly_configured = False
            result = None
        else:
            result = self._parse_scan_result(result_dict)

        return response, result
    
    def _report_result(self, xxx_todo_changeme):
        """
        This method stores the scan result in the KB, called as a callback for
        the _scan_http_response method.
        
        :param response: The HTTP response
        :param scan_result: The result object from _scan_http_response
        :return: None
        """
        (response, scan_result) = xxx_todo_changeme
        if scan_result is None:
            return

        if scan_result.found:
        
            desc = ('ClamAV identified malware at URL: "%s", the matched'
                    ' signature name is "%s".')
            desc %= (response.get_url(), scan_result.signature)
    
            i = Info('Malware identified', desc, response.id, self.get_name())
            i.set_url(response.get_url())
            
            self.kb_append(self, 'malware', i)

    def _parse_scan_result(self, result):
        """
        {'stream': ('FOUND', 'Eicar-Test-Signature')}
        {u'stream': (u'OK', None)}

        :return: A namedtuple with the scan result
        """
        try:
            signature = result['stream'][1]
            found = result['stream'][0] == 'FOUND'
            return ScanResult(found, signature)
        except:
            om.out.debug('Invalid response from clamd: %s' % result)

    def set_options(self, options_list):
        self._clamd_socket = options_list['clamd_socket'].get_value()

    def get_options(self):
        """
        :return: A list of option objects for this plugin.
        """
        ol = OptionList()

        d = 'ClamAV daemon socket path'
        h = ('Communication with ClamAV is performed over an Unix socket, in'
             ' order to be able to use this plugin please start a clamd daemon'
             ' and provide the unix socket path.')
        # TODO: Maybe I should change this STRING to INPUT_FILE?
        o = opt_factory('clamd_socket', self._clamd_socket, d, STRING, help=h)
        ol.add(o)

        return ol
    
    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        Uses ClamAV to identify malware in your site.
        
        In order to be able to use this plugin, you'll have to install ClamAV
        in your system, for Ubuntu the following commands should install ClamAV
        and start the daemon:
        
        sudo apt-get install clamav-daemon clamav-freshclam clamav-unofficial-sigs
        sudo freshclam
        sudo service clamav-daemon start
        
        To communicate with clamd the plugin uses an Unix socket, which can be
        configured by the user to point to the correct location.
       
        This plugin was sponsored by http://scoresecure.com/ .
        """


ScanResult = namedtuple('ScanResult', ['found', 'signature'])
