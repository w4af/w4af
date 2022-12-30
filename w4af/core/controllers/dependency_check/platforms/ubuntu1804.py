"""
ubuntu1804.py

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
import distro

from .ubuntu1604 import Ubuntu1604
from ..requirements import CORE, GUI


class Ubuntu1804(Ubuntu1604):
    SYSTEM_NAME = 'Ubuntu 18.04'

    CORE_SYSTEM_PACKAGES_18 = Ubuntu1604.CORE_SYSTEM_PACKAGES[:]
    CORE_SYSTEM_PACKAGES_18.remove('libssl-dev')
    CORE_SYSTEM_PACKAGES_18.append('libssl1.0-dev')
	
    GUI_SYSTEM_PACKAGEs_18 = Ubuntu1604.GUI_SYSTEM_PACKAGES[:]
    GUI_SYSTEM_PACKAGEs_18.remove('libssl-dev')
    GUI_SYSTEM_PACKAGEs_18.append('libssl1.0-dev')
    SYSTEM_PACKAGES = {CORE: CORE_SYSTEM_PACKAGES_18,
                       GUI: GUI_SYSTEM_PACKAGEs_18}

    def __init__(self):
        super(Ubuntu1804, self).__init__()

    @staticmethod
    def is_current_platform():
        return 'Ubuntu' in distro.name() and '18.04' in distro.version()

