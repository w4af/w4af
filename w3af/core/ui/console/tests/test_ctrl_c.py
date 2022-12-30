"""
test_ctrl_c.py

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
import signal
import subprocess
import time
import unittest
import tempfile

import pytest

from w4af import ROOT_PATH
from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.data.misc.encoding import smart_str_ignore


@pytest.mark.moth
@pytest.mark.fails
class TestHandleCtrlC(unittest.TestCase):
    
    SCRIPT = '%s/core/ui/console/tests/data/spider_long.w4af' % ROOT_PATH
    
    def prepare_script(self):
        fhandler = tempfile.NamedTemporaryFile(prefix='spider_long-',
                                               suffix='.w4af',
                                               dir=tempfile.tempdir,
                                               delete=False)
        with open(self.SCRIPT) as script:
            fhandler.write(smart_str_ignore(script.read() % {'moth': get_moth_http()}))
        fhandler.close()
        return fhandler.name
        
    @unittest.skip("Control flow issue - hard to debug")
    def test_scan_ctrl_c(self):
        script = self.prepare_script()
        cmd = ['python', 'w4af_console', '-s', script]

        process = subprocess.Popen(args=cmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=False,
                                   universal_newlines=True)
        
        # Let it run until the first new URL is found (and while the process
        # is still running)
        while process.poll() is None:
            w4af_output = process.stdout.readline()
            if 'New URL found by web_spider plugin' in w4af_output:
                time.sleep(1)
                break
        
        self.assertIs(process.poll(), None, 'w4af died before we could send Ctrl+C')
        
        # Send Ctrl+C
        process.send_signal(signal.SIGINT)

        EXPECTED = (
                    'User pressed Ctrl+C, stopping scan',
                    'The user stopped the scan.',
                    'w4af>>> exit',
                    )

        # set signal handler
        signal.signal(signal.SIGALRM, alarm_handler)
        # produce SIGALRM in X seconds
        signal.alarm(30)

        # In some cases process.stdout.read() simply hang for ever, so I want
        # to wait for 30 seconds (see signal.alarm) and then terminate the
        # process
        try:
            w4af_output = process.stdout.read()
            # cancel alarm
            signal.alarm(0)
        except Alarm:
            process.terminate()
            msg = 'w4af did not stop on Ctrl+C, read() timeout.'
            self.assertTrue(False, msg)
        
        for estr in EXPECTED:
            self.assertIn(estr, w4af_output)
            

        NOT_EXPECTED = ('The list of fuzzable requests is:',)

        for estr in NOT_EXPECTED:
            self.assertNotIn(estr, w4af_output)
        
        # We don't need this anymore...
        os.remove(script)

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm