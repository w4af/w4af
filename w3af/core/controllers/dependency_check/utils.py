"""
utils.py

Copyright 2006 Andres Riancho

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
import sys


def verify_python_version():
    """
    Check python version eq 2.6 or 2.7
    """
    major, minor, micro, release_level, serial = sys.version_info
    if major == 2:
        if minor != 7:
            msg = 'Error: Python 2.%s found but Python 2.7 required.'
            print((msg % minor))
    elif major > 3:
        msg = ('It seems that you are running w4af using Python4, which is not'
               ' officially supported by the w4af team.\n')
        print(msg)
        sys.exit(1)


def running_in_virtualenv():
    if hasattr(sys, 'real_prefix'):
        return True

    return False
