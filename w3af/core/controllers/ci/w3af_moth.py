"""
w3af_moth.py

Copyright 2015 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

HTTP_W3AF_MOTH = '/tmp/w3af-moth.txt'
DEFAULT_W3AF_MOTH = 'w3af-moth-fallback:80'


def get_w3af_moth_http(path='/'):
    try:
        with open(HTTP_W3AF_MOTH) as f:
            w3af_moth_netloc = f.read().strip()
    except IOError:
        w3af_moth_netloc = DEFAULT_W3AF_MOTH
    return 'http://%s%s' % (w3af_moth_netloc, path)



