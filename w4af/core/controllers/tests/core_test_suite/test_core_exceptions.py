"""
test_core_exceptions.py

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
import unittest

from unittest.mock import patch, call
import pytest

from w4af.core.data.parsers.doc.url import URL
from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.misc.factory import factory
from w4af.core.controllers.exceptions import (ScanMustStopException,
                                              ScanMustStopByUnknownReasonExc,
                                              ScanMustStopByUserRequest)
from w4af.plugins.tests.helper import create_target_option_list


@pytest.mark.moth
class TestCoreExceptions(unittest.TestCase):
    """
    TODO: Think about mocking all calls to ExtendedUrllib in order to avoid
          being tagged as 'moth'.
    """
    PLUGIN = 'w4af.core.controllers.tests.exception_raise'
    
    def setUp(self):
        """
        This is a rather complex setUp since I need to move the
        exception_raise.py plugin to the plugin directory in order to be able
        to run it afterwards.

        In the tearDown method, I'll remove the file.
        """
        self.w4afcore = w4afCore()
        
        target_opts = create_target_option_list(URL(get_moth_http()))
        self.w4afcore.target.set_options(target_opts)

        plugin_inst = factory(self.PLUGIN)
        plugin_inst.set_url_opener(self.w4afcore.uri_opener)
        plugin_inst.set_worker_pool(self.w4afcore.worker_pool)

        self.w4afcore.plugins.plugins['crawl'] = [plugin_inst]
        self.w4afcore.plugins._plugins_names_dict['crawl'] = ['exception_raise']
        self.exception_plugin = plugin_inst
        
        # Verify env and start the scan
        self.w4afcore.plugins.initialized = True
        self.w4afcore.verify_environment()        
    
    def tearDown(self):
        self.w4afcore.quit()
                        
    def test_stop_on_must_stop_exception(self):
        """
        Verify that the ScanMustStopException stops the scan.
        """
        self.exception_plugin.exception_to_raise = ScanMustStopException
        
        with patch('w4af.core.controllers.w4afCore.om.out') as om_mock:
            self.w4afcore.start()
            
            error = ('The following error was detected and could not be'
                     ' resolved:\nTest exception.\n')
            self.assertIn(call.error(error), om_mock.mock_calls)

    def test_stop_unknown_exception(self):
        """
        Verify that the ScanMustStopByUnknownReasonExc stops the scan.
        """
        self.exception_plugin.exception_to_raise = ScanMustStopByUnknownReasonExc
        self.assertRaises(ScanMustStopByUnknownReasonExc, self.w4afcore.start)
                
    def test_stop_by_user_request(self):
        """
        Verify that the ScanMustStopByUserRequest stops the scan.
        """
        self.exception_plugin.exception_to_raise = ScanMustStopByUserRequest
        
        with patch('w4af.core.controllers.w4afCore.om.out') as om_mock:
            self.w4afcore.start()
            
            message = 'Test exception.'
            self.assertIn(call.information(message), om_mock.mock_calls)