"""
test_strategy_low_level.py

Copyright 2013 Andres Riancho

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
import re
import unittest
import threading
import httpretty
from time import sleep

from unittest.mock import Mock
import pytest

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.core_helpers.strategy import CoreStrategy
from w4af.core.controllers.exceptions import ScanMustStopException
from w4af.core.data.kb.knowledge_base import kb


class TestStrategy(unittest.TestCase):
    
    TARGET_URL = get_moth_http('/audit/sql_injection/'
                               'where_integer_qs.py?id=1')
    EXPECTED_THREAD_NAMES = {
        'PoolTaskHandler',
        'PoolResultHandler',
        'OutputManagerWorkerThread',
        'PoolWorkerHandler',
        'MainThread',
        'SQLiteExecutor_0',
        'OutputManager',
        'QueueFeederThread'
    }

    def setUp(self):
        kb.cleanup()

    @pytest.mark.moth
    @pytest.mark.xfail
    def test_strategy_run(self):
        core = w4afCore()
        
        target = core.target.get_options()
        target['target'].set_value(self.TARGET_URL)
        core.target.set_options(target)
        
        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()
        
        core.verify_environment()
        core.scan_start_hook()
        
        def verify_threads_running(functor):
            thread_names = [t.name for t in threading.enumerate()]
            self.assertIn('WorkerThread', thread_names)
            self.called_teardown_audit = True
            return functor
        
        self.called_teardown_audit = False
        
        strategy = CoreStrategy(core)
        strategy._teardown_audit = verify_threads_running(strategy._teardown_audit)
        
        strategy.start()
        
        # Now test that those threads are being terminated
        self.assertTrue(self.called_teardown_audit)
        
        vulns = kb.get('sqli', 'sqli')
        self.assertEqual(len(vulns), 1, vulns)
        
        # Tell the core that we've finished, this should kill the WorkerThreads
        core.exploit_phase_prerequisites = lambda: 42
        core.scan_end_hook()

        self._assert_thread_names()

    def _get_running_threads(self):
        threads = [t for t in threading.enumerate()]
        thread_names = [t.name for t in threads]

        return set(thread_names)


    def _await_correct_thread_names(self):
        """
        Makes sure that the threads which are living in my process are the
        ones that I want.
        """
        thread_names_set = self._get_running_threads()

        wait = 0
        while self.EXPECTED_THREAD_NAMES != thread_names_set and wait < 30:
            print("Unexpected thread running... waiting for it to die")
            sleep(3)
            wait += 3

    def _assert_thread_names(self):
        """
        Makes sure that the threads which are living in my process are the
        ones that I want.
        """
        thread_names_set = self._get_running_threads()

        self.assertEqual(thread_names_set, self.EXPECTED_THREAD_NAMES)

    @pytest.mark.moth
    @pytest.mark.xfail
    def test_strategy_exception(self):
        self._await_correct_thread_names()

        core = w4afCore()
        
        target = core.target.get_options()
        target['target'].set_value(self.TARGET_URL)
        core.target.set_options(target)
        
        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()
        
        core.verify_environment()
        core.scan_start_hook()
        
        strategy = CoreStrategy(core)
        strategy._fuzzable_request_router = Mock(side_effect=Exception)
        
        strategy.terminate = Mock(wraps=strategy.terminate)
        
        self.assertRaises(Exception, strategy.start)
        
        # Now test that those threads are being terminated
        self.assertEqual(strategy.terminate.called, True)
        
        core.exploit_phase_prerequisites = lambda: 42
        core.scan_end_hook()

        self._assert_thread_names()
        
    def test_strategy_verify_target_server_up(self):
        core = w4afCore()
        
        # TODO: Change 2312 by an always closed/non-http port
        INVALID_TARGET = 'http://localhost:2312/'
        
        target = core.target.get_options()
        target['target'].set_value(INVALID_TARGET)
        core.target.set_options(target)
        
        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()
        
        core.verify_environment()
        core.scan_start_hook()
        
        strategy = CoreStrategy(core)
        
        try:
            strategy.start()
        except ScanMustStopException as wmse:
            message = str(wmse)
            self.assertIn('Please verify your target configuration', message)
        else:
            self.assertTrue(False)
        core.scan_end_hook()

        self._assert_thread_names()


    @httpretty.activate(allow_net_connect=False)
    def test_alert_if_target_is_301_all_proto_redir(self):
        """
        Tests that the protocol redirection is detected and reported in
        the kb
        """
        core = w4afCore()

        httpretty.register_uri(httpretty.GET,
                               re.compile("w4af.com/(.*)"),
                               body='301',
                               status=301,
                               adding_headers={'Location': 'https://w4af.com/'})

        target = core.target.get_options()
        target['target'].set_value('http://w4af.com/')
        core.target.set_options(target)

        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()

        core.verify_environment()
        core.scan_start_hook()

        strategy = CoreStrategy(core)
        strategy.start()

        infos = kb.get('core', 'core')
        self.assertEqual(len(infos), 1, infos)
        core.scan_end_hook()

        self._assert_thread_names()


    @httpretty.activate(allow_net_connect=False)
    def test_alert_if_target_is_301_all_domain_redir(self):
        """
        Tests that the domain redirection is detected and reported in
        the kb
        """
        core = w4afCore()

        httpretty.register_uri(httpretty.GET,
                               re.compile("w4af.com/(.*)"),
                               body='301',
                               status=301,
                               adding_headers={'Location': 'http://www.w4af.com/'})

        target = core.target.get_options()
        target['target'].set_value('http://w4af.com/')
        core.target.set_options(target)

        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()

        core.verify_environment()
        core.scan_start_hook()

        strategy = CoreStrategy(core)
        strategy.start()

        infos = kb.get('core', 'core')
        self.assertEqual(len(infos), 1, infos)
        core.scan_end_hook()

        self._assert_thread_names()


    @httpretty.activate(allow_net_connect=False)
    def test_alert_if_target_is_301_all_internal_redir(self):
        """
        Tests that no info is created if the site redirects internally
        """
        core = w4afCore()

        httpretty.register_uri(httpretty.GET,
                               re.compile("w4af.com/(.*)"),
                               body='301',
                               status=301,
                               adding_headers={'Location': 'http://w4af.com/xyz'})

        target = core.target.get_options()
        target['target'].set_value('http://w4af.com/')
        core.target.set_options(target)

        core.plugins.set_plugins(['sqli'], 'audit')
        core.plugins.init_plugins()

        core.verify_environment()
        core.scan_start_hook()

        strategy = CoreStrategy(core)
        strategy.start()

        infos = kb.get('core', 'core')
        self.assertEqual(len(infos), 0, infos)
        core.scan_end_hook()

        self._assert_thread_names()