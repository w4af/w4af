"""
test_w4af_gui.py

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
import unittest
import signal
from unittest.mock import patch
import py_compile
import os
from subprocess import Popen, PIPE

class TimeoutException(Exception):
    pass

class Testw4afGUI(unittest.TestCase):
    def test_compiles(self):
        try:
            py_compile.compile('w4af_gui', '/tmp/foo.tmp', 'exec')
        except SyntaxError as se:
            self.assertTrue(False, 'Error in w4af_gui code "%s"' % se)

    def get_working_dir(self, filename: str) -> str:
        filename = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            '..', '..', '..', '..', "w4af_gui"))
        self.assertTrue(os.path.isfile(filename))
        return os.path.dirname(filename)

    def test_handles_command_line_args(self):
        success = False

        def timeout_handler(signum, frame):
            self.assertTrue(success, "Expected GUI not to launch")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(4)
        try:
            process = Popen(['./w4af_gui', '-h'], stdout=PIPE, stderr=PIPE, cwd=self.get_working_dir('w4af_gui'))
            stdout, stderr = process.communicate()
            self.assertTrue(b"usage: w4af_gui" in stdout)
            self.assertTrue(b"Web Interface for w4af" in stdout, stdout)
            signal.alarm(0)
        except TimeoutException:
            timeout_handler(0, 0)

    def test_expect_developer_option(self):
        success = False

        def timeout_handler(signum, frame):
            self.assertTrue(success, "Expected GUI not to launch")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(4)
        try:
            process = Popen(['./w4af_gui'], stdout=PIPE, stderr=PIPE, cwd=self.get_working_dir('w4af_gui'))
            stdout, stderr = process.communicate()
            self.assertTrue(b"usage: w4af_gui" in stdout)
            self.assertTrue(b"i-am-a-developer" in stdout, stdout)
            success = True
            signal.alarm(0)
        except TimeoutException:
            timeout_handler(0, 0)