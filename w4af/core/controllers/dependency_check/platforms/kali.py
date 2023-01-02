"""
kali.py

Copyright 2014 Andres Riancho

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
import distro 

from .ubuntu1204 import Ubuntu1204

KALI_MESSAGE = '''
According to Kali's documentation [0] in order to avoid breaking the packaged\
 w4af version you should run the following commands:

cd ~
apt-get install -y python-pip
pip install --upgrade pip
git clone https/github.com/w4af/w4af.git
cd w4af
./w4af_console
. /tmp/w4af_dependency_install.sh

[0] http://www.kali.org/kali-monday/bleeding-edge-kali-repositories/
'''


class Kali(Ubuntu1204):
    SYSTEM_NAME = 'Kali'

    @staticmethod
    def after_hook():
        print(KALI_MESSAGE)

    @staticmethod
    def is_current_platform():
        return 'debian' in distro.id() and 'kali' in distro.name()

