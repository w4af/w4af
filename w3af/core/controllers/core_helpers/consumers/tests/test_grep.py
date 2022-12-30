"""
test_grep.py

Copyright 2019 Andres Riancho

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
import unittest

import w4af.core.data.kb.config as cf

from w4af import ROOT_PATH
from w4af.core.controllers.core_helpers.consumers.grep import grep
from w4af.plugins.grep.code_disclosure import code_disclosure
from w4af.core.controllers.w4afCore import w4afCore
from w4af.tests.helpers.parse_http_log import iter_http_request_responses


class TestGrepConsumer(unittest.TestCase):

    HTTP_FILE = os.path.join(ROOT_PATH, '..', 'scan-logs', 'kryptera-ktCKJ.http')
    MAX_REQUEST_RESPONSE = 5000
    CACHE_TEST_EVERY = 50
    CACHE_TESTS = 5

    def test_should_grep_speed(self):
        """
        This method tests the performance of the should_grep method

        This method is usually run as:

            kernprof -o nose.lprof -v -l nosetests -s -v w4af/core/controllers/core_helpers/consumers/tests/test_grep.py

        Remember to:

            * Specify a valid file in HTTP_FILE (generated during a scan)
            * Decorate the methods you want to analyze with @profile

        """
        if not os.path.exists(self.HTTP_FILE):
            return

        grep_plugins = [code_disclosure()]
        core = w4afCore()

        grep_consumer = grep(grep_plugins, core)

        for count, (request, response) in enumerate(iter_http_request_responses(self.HTTP_FILE)):

            if not cf.cf.get('target_domains'):
                cf.cf.save('target_domains', {request.get_uri().get_domain()})

            grep_consumer.should_grep(request, response)

            if count % self.CACHE_TEST_EVERY == 0:
                for _ in range(self.CACHE_TESTS):
                    grep_consumer.should_grep(request, response)

            if count >= self.MAX_REQUEST_RESPONSE:
                break
