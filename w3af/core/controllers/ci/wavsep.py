"""
wavsep.py

Copyright 2014 Andres Riancho

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

HTTP_WAVSEP = '/tmp/wavsep.txt'
DEFAULT_WAVSEP = 'wavsep-fallback:80'


def get_wavsep_http(path='/'):
    try:
        with open(HTTP_WAVSEP) as f:
            wavsep_netloc = f.read().strip()
    except IOError:
        wavsep_netloc = DEFAULT_WAVSEP

    return 'http://%s%s' % (wavsep_netloc, path)

