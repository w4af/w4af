"""
test_multiple_instances.py

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
import threading

from multiprocessing.dummy import DummyProcess
import pytest

from w4af.core.controllers.w4afCore import w4afCore


def start_w4af_core(exception_handler):
    try:
        w4afCore()
    except Exception as e:
        if exception_handler:
            exception_handler(e)


@pytest.mark.smoke
class Testw4afCore(unittest.TestCase):

    def setUp(self):
        self._exceptions = []

    def _exception_handler(self, exp):
        self._exceptions.append(exp)

    def test_multiple_instances(self):
        """
        Just making sure nothing crashes if I have more than 1 instance of
        w4afCore
        """
        instances = []
        for _ in range(5):
            instances.append(w4afCore())

    def test_multiple_instances_in_different_dummy_processes(self):
        """
        Create different w4afCore instances, in different threads.

        https://github.com/andresriancho/w4af-module/issues/5
        """
        t = DummyProcess(target=start_w4af_core,
                         args=(self._exception_handler,))
        t.start()
        t.join()

        self.assertEqual(self._exceptions, [])

    def test_dummy_in_dummy(self):
        """
        Create different w4afCore instances, in different threads.

        https://github.com/andresriancho/w4af-module/issues/5
        """
        def outer():
            t = DummyProcess(target=start_w4af_core,
                             args=(self._exception_handler,))
            t.start()
            t.join()

        t = DummyProcess(target=outer)
        t.start()
        t.join()

        self.assertEqual(self._exceptions, [])

    def test_dummy_in_thread(self):
        """
        Remember me?
        AttributeError: 'Worker' object has no attribute '_children'

        http://bugs.python.org/issue14881
        """
        def outer():
            try:
                t = DummyProcess(target=start_w4af_core,
                                 args=(self._exception_handler,))
                t.start()
            except AttributeError:
                pass

        t = threading.Thread(target=outer)
        t.start()
        t.join()

        self.assertEqual(self._exceptions, [])
