"""
test_audit.py

Copyright 2018 Andres Riancho

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
import httpretty

from unittest.mock import patch, call

import w4af.core.data.kb.knowledge_base as kb

from w4af.core.controllers.core_helpers.consumers.audit import audit
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.exceptions import ScanMustStopException
from w4af.plugins.audit.xss import xss
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL

import pytest

class TestAuditConsumer(unittest.TestCase):

    def tearDown(self):
        kb.kb.cleanup()

    @httpretty.activate
    def test_teardown_with_must_stop_exception(self):
        w4af_core = w4afCore()

        xss_instance = xss()
        xss_instance.set_url_opener(w4af_core.uri_opener)
        xss_instance.set_worker_pool(w4af_core.worker_pool)

        audit_plugins = [xss_instance]

        audit_consumer = audit(audit_plugins, w4af_core)
        audit_consumer.start()

        url = 'http://w4af.org/?id=1'

        httpretty.register_uri(httpretty.GET, url,
                               body='hello world',
                               content_type='application/html')

        url = URL(url)
        fr = FuzzableRequest(url)

        # This will trigger a few HTTP requests to the target URL which will
        # also initialize all the xss plugin internals to be able to run end()
        # later.
        audit_consumer.in_queue_put(fr)
        kb.kb.add_fuzzable_request(fr)

        # Now that xss.audit() was called, we want to simulate network errors
        # that will put the uri opener in a state where it always answers with
        # ScanMustStopException
        w4af_core.uri_opener._stop_exception = ScanMustStopException('mock')

        # And now we just call terminate() which injects the poison pill and will
        # call teardown, which should call xss.end(), which should try to send HTTP
        # requests, which will raise a ScanMustStopException
        with patch('w4af.core.controllers.core_helpers.consumers.audit.om.out') as om_mock:
            audit_consumer.terminate()

            msg1 = ('Spent 0.00 seconds running xss.end() until a scan must'
                   ' stop exception was raised')
            msg2 = ('Spent 0.01 seconds running xss.end() until a scan must'
                   ' stop exception was raised')
            if call.debug(msg1) in om_mock.mock_calls:
                self.assertIn(call.debug(msg1), om_mock.mock_calls)
            else:
                self.assertIn(call.debug(msg2), om_mock.mock_calls)

        w4af_core.quit()
