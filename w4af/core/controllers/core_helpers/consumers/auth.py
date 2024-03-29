"""
auth.py

Copyright 2012 Andres Riancho

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
import queue

import w4af.core.controllers.output_manager as om

from .base_consumer import BaseConsumer, task_decorator
from .constants import POISON_PILL, FORCE_LOGIN
from w4af.core.data.fuzzer.utils import rand_alnum
from w4af.core.controllers.profiling.took_helper import TookLine


class auth(BaseConsumer):
    """
    Thread that logins into the application every N seconds.
    """

    def __init__(self, auth_plugins, w4af_core, timeout):
        """
        :param auth_plugins: Instances of auth plugins in a list
        :param w4af_core: The w4af core that we'll use for status reporting
        :param timeout: The time to wait between each login check
        """
        super(auth, self).__init__(auth_plugins, w4af_core,
                                   thread_name=self.get_name(),
                                   create_pool=False)

        self._timeout = timeout

    def get_name(self):
        return 'Authenticator'

    def run(self):
        """
        Consume the queue items
        """
        while True:

            try:
                action = self.in_queue.get(timeout=self._timeout)
            except KeyboardInterrupt:
                # https://github.com/andresriancho/w3af/issues/9587
                #
                # If we don't do this, the thread will die and will never
                # process the POISON_PILL, which will end up in an endless
                # wait for .join()
                continue
            except queue.Empty:
                # pylint: disable=E1120
                self._login()
                # pylint: enable=E1120
            else:

                if action == POISON_PILL:

                    try:
                        self._end_plugins()
                    finally:
                        self.in_queue.task_done()
                        self.set_has_finished()
                        break

                elif action == FORCE_LOGIN:
                    # pylint: disable=E1120
                    try:
                        self._login()
                    finally:
                        self.in_queue.task_done()
                    # pylint: enable=E1120

    def _end_plugins(self):
        for plugin in self._consumer_plugins:
            plugin.end()

    # Adding task here because we want to let the rest of the world know
    # that we're still doing something. The _task_done below will "undo"
    # this action.
    @task_decorator
    def _login(self, function_id):
        """
        This is the method that actually calls the plugins in order to login
        to the web application.
        """
        for plugin in self._consumer_plugins:

            debugging_id = rand_alnum(8)
            args = (plugin.get_name(), plugin.get_name(), debugging_id)
            msg = 'auth consumer is calling %s.has_active_session() and %s.login() (did:%s)'

            om.out.debug(msg % args)

            took_line = TookLine(self._w4af_core,
                                 'auth',
                                 '_login',
                                 debugging_id=debugging_id)

            try:
                if not plugin.has_active_session(debugging_id=debugging_id):
                    plugin.login(debugging_id=debugging_id)
            except Exception as e:
                self.handle_exception('auth', plugin.get_name(), None, e)

            took_line.send()

    def async_force_login(self):
        self.in_queue_put(FORCE_LOGIN)

    def force_login(self):
        # pylint: disable=E1120
        self._login()
        # pylint: enable=E1120
