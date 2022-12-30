"""
test_core_integration.py

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
import pytest
import unittest

from unittest.mock import MagicMock

from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.data.parsers.doc.url import URL
from w4af.plugins.tests.helper import create_target_option_list


@pytest.mark.moth
class TestCoreIntegration(unittest.TestCase):
    
    def setUp(self):
        self.w4afcore = w4afCore()

    def tearDown(self):
        self.w4afcore.quit()
            
    def test_send_mangled(self):
        
        self.w4afcore.plugins.set_plugins(['self_reference'], 'evasion')
        self.w4afcore.plugins.set_plugins(['sqli'], 'audit')
        
        target_opts = create_target_option_list(URL(get_moth_http()))
        self.w4afcore.target.set_options(target_opts)

        # Verify env and start the scan
        self.w4afcore.plugins.init_plugins()
        self.w4afcore.verify_environment()
        
        sref = self.w4afcore.plugins.plugins['evasion'][0]
        
        def return_arg(request):
            return request
        sref.modify_request = MagicMock(side_effect=return_arg)
        
        self.w4afcore.start()
        
        self.assertGreater(sref.modify_request.call_count, 15)