"""
retirejs.py

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
import subprocess

from w4af.core.controllers.misc.which import which


SUPPORTED_RETIREJS = b'3.'


def retirejs_is_installed():
    """
    :return: True if retirejs is installed and we were able to parse the version.
    """
    try:
        version = subprocess.check_output('npx retire --version', shell=True)
    except subprocess.CalledProcessError:
        return False

    version = version.strip()
    version_split = version.split(b'.')

    # Just check that the version has the format 1.6.0
    if len(version_split) != 3:
        return False

    if not version.startswith(SUPPORTED_RETIREJS):
        return False

    return True
