"""
error_pages.py

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
import w4af.core.data.kb.knowledge_base as kb

from w4af.core.data.db.disk_list import DiskList
from w4af.core.data.quick_match.multi_in import MultiIn
from w4af.core.data.quick_match.multi_re import MultiRE
from w4af.core.data.kb.info import Info
from w4af.core.controllers.plugins.grep_plugin import GrepPlugin
from w4af.core.data.misc.encoding import smart_str_ignore


class error_pages(GrepPlugin):
    """
    Grep every page for error pages.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    ERROR_PAGES = (
        b'<H1>Error page exception</H1>',

        # This signature fires up also in default 404 pages of aspx which
        # generates a lot of noise, so ... disabling it
        # '<span><H1>Server Error in ',

        b'<h2> <i>Runtime Error</i> </h2></span>',
        b'<h2> <i>Access is denied</i> </h2></span>',
        b'<H3>Original Exception: </H3>',
        b'Server object error',
        b'invalid literal for int()',
        b'exceptions.ValueError',

        b'<font face="Arial" size=2>Type mismatch: ',
        b'[an error occurred while processing this directive]',

        b'<HTML><HEAD><TITLE>Error Occurred While Processing Request</TITLE>'
        b'</HEAD><BODY><HR><H3>Error Occurred While Processing Request</H3><P>',

        # VBScript
        b'<p>Microsoft VBScript runtime </font>',
        b"<font face=\"Arial\" size=2>error '800a000d'</font>",

        # nwwcgi errors
        b'<TITLE>nwwcgi Error',

        # ASP error I found during a pentest, the ASP used a foxpro db, not a
        # SQL injection
        b'<font face="Arial" size=2>error \'800a0005\'</font>',
        b'<h2> <i>Runtime Error</i> </h2></span>',
        # Some error in ASP when using COM objects.
        b'Operation is not allowed when the object is closed.',
        # An error when ASP tries to include something and it fails
        b'<p>Active Server Pages</font> <font face="Arial" size=2>error \'ASP 0126\'</font>',

        # ASPX
        b'<b> Description: </b>An unhandled exception occurred during the execution of the'
        b' current web request',

        # Struts
        b'] does not contain handler parameter named',

        # PHP
        b'<b>Warning</b>: ',
        b'No row with the given identifier',
        b'open_basedir restriction in effect',
        b"eval()'d code</b> on line <b>",
        b"Cannot execute a blank command in",
        b"Fatal error</b>:  preg_replace",
        b"thrown in <b>",
        b"#0 {main}",
        b"Stack trace:",
        b"</b> on line <b>",

        # python
        b"PythonHandler django.core.handlers.modpython",
        b"t = loader.get_template(template_name) # You need to create a 404.html template.",
        b'<h2>Traceback <span>(innermost last)</span></h2>',

        # Java
        b'[java.lang.',
        b'class java.lang.',
        b'java.lang.NullPointerException',
        b'java.rmi.ServerException',
        b'at java.lang.',

        b'onclick="toggle(\'full exception chain stacktrace\')"',
        b'at org.apache.catalina',
        b'at org.apache.coyote.',
        b'at org.apache.tomcat.',
        b'at org.apache.jasper.',

        # https://github.com/andresriancho/w3af/issues/4001
        b'<html><head><title>Application Exception</title>',

        # ruby
        b'<h1 class="error_title">Ruby on Rails application could not be started</h1>',

        # Coldfusion
        b'<title>Error Occurred While Processing Request</title></head><body><p></p>',
        b'<HTML><HEAD><TITLE>Error Occurred While Processing Request</TITLE></HEAD><BODY><HR><H3>',
        b'<TR><TD><H4>Error Diagnostic Information</H4><P><P>',

        b'<li>Search the <a href="http://www.macromedia.com/support/coldfusion/" '
        b'target="new">Knowledge Base</a> to find a solution to your problem.</li>',

        # http://www.programacion.net/asp/articulo/kbr_execute/
        b'Server.Execute Error',

        # IIS
        b'<h2 style="font:8pt/11pt verdana; color:000000">HTTP 403.6 - Forbidden: IP address rejected<br>',
        b'<TITLE>500 Internal Server Error</TITLE>',
    )
    _multi_in = MultiIn(ERROR_PAGES)

    VERSION_REGEX = (
        (rb'<address>(.*?)</address>', 'Apache'),
        (rb'<HR size="1" noshade="noshade"><h3>(.*?)</h3></body>',
         'Apache Tomcat'),
        (rb'<a href="http://www.microsoft.com/ContentRedirect.asp\?prd=iis&sbp=&pver=(.*?)&pid=&ID', 'IIS'),

        # <b>Version Information:</b>&nbsp;Microsoft .NET Framework Version:1.1.4322.2300; ASP.NET Version:1.1.4322.2300
        (rb'<b>Version Information:</b>&nbsp;(.*?)\n', 'ASP .NET')
    )
    _multi_re = MultiRE(VERSION_REGEX)

    MAX_REPORTED_PER_MSG = 10

    def __init__(self):
        GrepPlugin.__init__(self)

        #   Internal variables
        self._potential_vulns = DiskList(table_prefix='error_pages')

        self._already_reported_max_msg_exceeded = []
        self._already_reported_versions = []
        self._compiled_regex = []

    def grep(self, request, response):
        """
        Plugin entry point, find the error pages and report them.

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        """
        if not response.is_text_or_html():
            return
        
        self.find_error_page(request, response)
        self.find_version_numbers(request, response)
    
    def find_error_page(self, request, response):
        # There is no need to report more than one info for the
        # same result, the user will read the info object and
        # analyze it even if we report it only once. If we report
        # it twice, he'll get mad ;)
        for _, _, _, url, _ in self._potential_vulns:
            if url == response.get_url():
                return

        for msg in self._multi_in.query(smart_str_ignore(response.body)):
            if self._avoid_report(request, response, msg):
                continue

            # We found a new error in a response!
            desc = 'The URL: "%s" contains the descriptive error: "%s".'
            desc %= (response.get_url(), msg)

            title = 'Descriptive error page'

            data = (title, desc, response.id, response.get_url(), msg)
            self._potential_vulns.append(data)

            # Just report one instance for each HTTP response, no
            # matter if multiple strings match
            break

    def _avoid_report(self, request, response, msg):
        # We should avoid multiple reports for the same error message
        # the idea here is that the root cause for the same error
        # message might be the same, and fixing one will fix all.
        #
        # So the user receives the first report with MAX_REPORTED_PER_MSG
        # vulnerabilities, fixes the root cause, scans again and then
        # all those instances go away.
        #
        # Without this code, the scanner will potentially report
        # thousands of issues for the same error message. Which will
        # overwhelm the user.
        count = 0

        for title, desc, _id, url, highlight in self._potential_vulns:
            if highlight == msg:
                count += 1

        if count < self.MAX_REPORTED_PER_MSG:
            return False

        if msg not in self._already_reported_max_msg_exceeded:
            self._already_reported_max_msg_exceeded.append(msg)

            desc = ('The application returned multiple HTTP responses'
                    ' containing detailed error pages containing exceptions'
                    ' and internal information. The maximum number of'
                    ' vulnerabilities for this issue type was reached'
                    ' and no more issues will be reported.')

            i = Info('Multiple descriptive error pages', desc, [], self.get_name())
            self.kb_append_uniq(self, 'error_page', i)

        return True

    def end(self):
        """
        This method is called when the plugin wont be used anymore.
        """
        for title, desc, _id, url, highlight in self._potential_vulns:
            for info in kb.kb.get_all_findings_iter():
                # This makes sure that if the sqli plugin found a vulnerability
                # in the same URL as we found a detailed error, we won't report
                # the detailed error.
                #
                # If the user fixes the sqli vulnerability and runs the scan again
                # most likely the detailed error will disappear too. If the sqli
                # vulnerability disappears and this one remains, it will appear
                # as a new vulnerability in the second scan.
                if info.get_url() == url:
                    break
            else:
                i = Info(title, desc, _id, self.get_name())
                i.set_url(url)
                i.add_to_highlight(highlight)

                self.kb_append_uniq(self, 'error_page', i)

        self._potential_vulns.cleanup()

    def find_version_numbers(self, request, response):
        """
        Now i'll check if I can get a version number from the error page
        This is common in apache, tomcat, etc...
        """
        if 400 < response.get_code() < 600:

            for match, _, _, server in self._multi_re.query(response.body):
                match_string = match.group(0)
                if match_string not in self._already_reported_versions:
                    # Save the info obj
                    desc = 'An error page sent this %s version: "%s".'
                    desc %= (server, match_string)

                    i = Info('Error page with information disclosure',
                             desc, response.id, self.get_name())
                    i.set_url(response.get_url())
                    i.add_to_highlight(server)
                    i.add_to_highlight(match_string)
                    
                    kb.kb.append(self, 'server', i)
                    kb.kb.raw_write(self, 'server', match_string)
                    
                    self._already_reported_versions.append(match_string)

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin scans every page for error pages, and if possible extracts
        the web server or programming framework information.
        """
