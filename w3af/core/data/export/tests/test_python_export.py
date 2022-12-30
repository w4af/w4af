"""
test_python_export.py

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
import unittest
import py_compile
import tempfile
import os

from w4af.core.data.export.python_export import python_export

EXPECTED_SIMPLE = """import urllib.request

url = "http://www.w4af.org/"
data = None
headers = {
    "Host" : "www.w4af.org",
    "Foo" : "bar"
}

request = urllib.request.Request(url, data, headers)
response = urllib.request.urlopen(request)
response_body = response.read()
print(response_body)
"""

EXPECTED_POST = """import urllib.request

url = "http://www.w4af.org/"
data = b"a=1"
headers = {
    "Host" : "www.w4af.org",
    "Content-Type" : "application/x-www-form-urlencoded"
}

request = urllib.request.Request(url, data, headers)
response = urllib.request.urlopen(request)
response_body = response.read()
print(response_body)
"""

EXPECTED_POST_REPEATED = """import urllib.request

url = "http://www.w4af.org/"
data = b"a=1&a=2"
headers = {
    "Host" : "www.w4af.org",
    "Content-Type" : "application/x-www-form-urlencoded",
    "Foo" : "spam, eggs"
}

request = urllib.request.Request(url, data, headers)
response = urllib.request.urlopen(request)
response_body = response.read()
print(response_body)
"""


class TestPythonExport(unittest.TestCase):

    def can_compile(self, source_code):
        file = tempfile.NamedTemporaryFile("w", delete=False)
        name = file.name
        file.write(source_code)
        file.close()
        target_file = os.path.join(tempfile.gettempdir(), "compile_temp.pyc")
        try:
            res = py_compile.compile(name, cfile=target_file, doraise=True)
            return True
        finally:
            if os.path.exists(target_file):
                os.unlink(target_file)
            os.unlink(name)

    def test_export_GET(self):
        http_request = 'GET http://www.w4af.org/ HTTP/1.1\n' \
                       'Host: www.w4af.org\n' \
                       'Foo: bar\n' \
                       '\n'
        python_code = python_export(http_request)
        self.assertTrue(self.can_compile(python_code))
        self.assertEqual(python_code, EXPECTED_SIMPLE)

    def test_export_POST(self):
        http_request = 'POST http://www.w4af.org/ HTTP/1.1\n' \
                       'Host: www.w4af.org\n' \
                       'Content-Length: 3\n' \
                       'Content-Type: application/x-www-form-urlencoded\n' \
                       '\n' \
                       'a=1'
        python_code = python_export(http_request)
        self.assertTrue(self.can_compile(python_code))
        self.assertEqual(python_code, EXPECTED_POST)

    def test_export_POST_repeated(self):
        http_request = 'POST http://www.w4af.org/ HTTP/1.1\n' \
                       'Host: www.w4af.org\n' \
                       'Content-Length: 7\n' \
                       'Content-Type: application/x-www-form-urlencoded\n' \
                       'Foo: spam\n' \
                       'Foo: eggs\n' \
                       '\n' \
                       'a=1&a=2'
        python_code = python_export(http_request)
        self.assertTrue(self.can_compile(python_code))
        self.assertEqual(python_code, EXPECTED_POST_REPEATED)

    def test_export_inject(self):
        http_request = 'POST http://www.w4af.org/ HTTP/1.1\n' \
                       'Host: www.w4af.org\n' \
                       'Content-Length: 7\n' \
                       'Content-Type: application/x-www-form-urlencoded\n' \
                       'Foo: sp"am\n' \
                       'Foo: eggs\n' \
                       '\n' \
                       'a=1&a=2"3'
        python_code = python_export(http_request)
        self.assertTrue(self.can_compile(python_code))
        self.assertIn('a=1&a=2%223', python_code)
        self.assertIn("sp\\\"am", python_code)
