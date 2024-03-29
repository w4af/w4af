"""
autocomplete.py

Copyright 2019 Andres Riancho

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
import w4af.core.data.parsers.parser_cache as parser_cache

from w4af.core.controllers.plugins.auth_session_plugin import AuthSessionPlugin
from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.data.options.opt_factory import opt_factory
from w4af.core.data.options.option_list import OptionList
from w4af.core.data.dc.factory import dc_from_form_params
from w4af.core.data.options.option_types import URL as URL_OPT, STRING
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.request.fuzzable_request import FuzzableRequest


class autocomplete(AuthSessionPlugin):
    """
    Fill and submit login forms
    """

    def __init__(self):
        AuthSessionPlugin.__init__(self)

        # User configured settings
        self.username = ''
        self.password = ''
        self.login_form_url = URL('http://host.tld/login')
        self.check_url = URL('http://host.tld/check')
        self.check_string = ''

    def login(self, debugging_id=None):
        """
        Login to the application:
            * HTTP GET `login_form_url`
            * Parse the HTML in `login_form_url` and find the login form
            * Fill the form with the user-configured credentials
            * Submit the form
        """
        #
        # In some cases the authentication plugin is incorrectly configured and
        # we don't want to keep trying over and over to login when we know it
        # will fail
        #
        if not self._attempt_login:
            return False

        # Create a new debugging ID for each login() run
        self._set_debugging_id(debugging_id)
        self._clear_log()

        msg = 'Logging into the application with user: %s' % self.username
        self._log_debug(msg)

        #
        # First we send the request to `login_form_url` and then we extract
        # the HTML form. If there are any problems in this step, just skip
        # the next calls to login()
        #
        form = self._get_login_form()

        if not form:
            self._handle_authentication_failure()
            return False

        #
        # Complete the parameters and send the form to the server
        #
        form_submitted = self._submit_form(form)

        if not form_submitted:
            self._handle_authentication_failure()
            return False

        #
        # Check if we're logged in
        #
        if self.has_active_session(debugging_id=debugging_id):
            self._handle_authentication_success(form)
            return True

        self._handle_authentication_failure()
        return False

    def logout(self):
        """
        User logout
        """
        return None

    def _handle_authentication_success(self, form):
        super(autocomplete, self)._handle_authentication_success()

        form_url = form.get_action().uri2url()

        args = (self.username, form_url)
        msg = 'Login success for username %s with form action %s'
        self._log_debug(msg % args)

        self._configure_audit_blacklist(form_url)

    def _submit_form(self, form_params):
        """
        Complete the username and password in the form fields and submit it
        to the server.

        :param form_params: The form parameters as returned by the HTML parser
        :return: True if form was submitted to the server
        """
        #
        # Create a form instance, using the proper encoding (multipart
        # or url). The form_params instance only has the parameters and can
        # not be sent to the wire.
        #
        form = dc_from_form_params(form_params)

        form.set_login_username(self.username)
        form.set_login_password(self.password)

        #
        # Transform to a fuzzable request and send to the wire
        #
        fuzzable_request = FuzzableRequest.from_form(form)

        try:
            http_response = self._uri_opener.send_mutant(fuzzable_request,
                                                         grep=False,
                                                         cache=False,
                                                         follow_redirects=True,
                                                         debugging_id=self._debugging_id)
        except Exception as e:
            msg = 'Failed to submit the login form: %s'
            self._log_debug(msg % e)
            return False

        msg = 'Login form sent to %s in HTTP request ID %s'
        args = (fuzzable_request.get_uri(), http_response.id,)
        self._log_debug(msg % args)

        self._log_http_response(http_response)

        return True

    def _get_login_form(self):
        """
        Parse the HTML returned from `login_form_url` and find the HTML form
        that can be used to login to the application.

        :return: A Form instance
        """
        #
        # Send the HTTP GET request to retrieve the HTML
        #
        try:
            http_response = self._uri_opener.GET(self.login_form_url,
                                                 grep=False,
                                                 cache=False,
                                                 follow_redirects=True,
                                                 debugging_id=self._debugging_id)
        except Exception as e:
            msg = 'Failed to HTTP GET the login_form_url: %s'
            self._log_debug(msg % e)
            return

        self._log_http_response(http_response)

        #
        # Extract the form from the HTML document
        #
        try:
            document_parser = parser_cache.dpc.get_document_parser_for(http_response)
        except BaseFrameworkException as e:
            msg = 'Failed to find a parser for the login_form_url: %s'
            self._log_debug(msg % e)
            return

        login_form = None

        for form_params in document_parser.get_forms():
            #
            # Find a form that:
            #
            #   * Is a login form
            #   * The action points to the target domain
            #   * This is the only login form in the page
            #
            if not form_params.is_login_form():
                continue

            if form_params.get_action().get_domain() != self.login_form_url.get_domain():
                continue

            if login_form is not None:
                #
                # There are two or more login forms in this page
                #
                self._log_debug('There are two or more login forms in the login_form_url.'
                                ' This is not supported by the autocomplete authentication'
                                ' plugin, will use the first identified form and ignore the'
                                ' second one.')
                continue

            login_form = form_params

        if login_form is None:
            msg = ('Failed to find an HTML login form at %s (id: %s).'
                   ' The authentication plugin is most likely incorrectly configured.')
            args = (self.login_form_url, http_response.id)
            self._log_error(msg % args)

            #
            # We get here when:
            #
            #   * The user configured the login form URL incorrectly
            #
            #   * There is an error in the HTTP request, and the HTTP response
            #     does NOT contain the login form.
            #
            # It is impossible to know in which case we are in, so we just return
            # None and wait for the next call to login(). The next call will act
            # as the retry strategy for the potential HTTP request / response error
            #
            # In the past we were setting self._attempt_login = False here, but
            # any errors (timeouts!) in the HTTP request to get the form ended
            # up in an ugly situation where the plugin was disabled
            #
            return None

        msg = 'Login form with action %s found in HTTP response with ID %s'
        args = (login_form.get_action(), http_response.id,)
        self._log_debug(msg % args)

        return login_form

    def _get_main_authentication_url(self):
        return self.login_form_url

    def get_options(self):
        """
        :return: A list of option objects for this plugin.
        """
        options = [
            ('username', self.username, STRING,
             'Username for the authentication process'),

            ('password', self.password, STRING,
             'Password for the authentication process'),

            ('login_form_url', self.login_form_url, URL_OPT,
             'The URL where the login form appears'),

            ('check_url', self.check_url, URL_OPT,
             'URL used to verify if the session is active. The plugin sends'
             ' an HTTP GET request to this URL and asserts if `check_string`'
             ' is present.'),

            ('check_string', self.check_string, STRING,
             'String to search in the `check_url` page to determine if the'
             ' session is active.'),
        ]

        ol = OptionList()

        for o in options:
            ol.add(opt_factory(o[0], o[1], o[3], o[2], help=o[3]))

        return ol

    def set_options(self, options_list):
        """
        This method sets all the options that are configured using
        the user interface generated by the framework using
        the result of get_options().

        :param options_list: A dict with the options for the plugin.
        :return: No value is returned.
        """
        self.username = options_list['username'].get_value()
        self.password = options_list['password'].get_value()
        self.check_string = options_list['check_string'].get_value()
        self.login_form_url = options_list['login_form_url'].get_value()
        self.check_url = options_list['check_url'].get_value()

        missing_options = []

        for o in options_list:
            if not o.get_value():
                missing_options.append(o.get_name())

        if missing_options:
            msg = ('All plugin configuration parameters are required.'
                   ' The missing parameters are: %s')
            raise BaseFrameworkException(msg % ', '.join(missing_options))

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This authentication plugin can login to Web applications which use
        common authentication schemes, including those which use CSRF tokens.

        The plugin performs an HTTP GET request on `login_form_url` to obtain
        the HTML form parameters and values, fills the `username` and
        `password` fields and then submits the form (usually with HTTP POST)
        to authenticate the user. 

        The following configurable parameters exist:
            - username
            - password
            - login_form_url
            - check_url
            - check_string
        """
