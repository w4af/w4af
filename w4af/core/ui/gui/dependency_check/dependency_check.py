"""
dependency_check.py

Copyright 2013 Andres Riancho

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

from w4af.core.controllers.misc.which import which
from w4af.core.controllers.dependency_check.dependency_check import dependency_check as mdep_check
from w4af.core.controllers.dependency_check.platforms.base_platform import GUI


def dependency_check():
    """
    This dependency check function uses the information stored in the platforms
    module to call the function in core.controllers.dependency_check which
    actually checks for the dependencies.
    
    The data in the core.ui.gui.dependency_check.platforms module is actually
    based on the data stored in core.controllers.dependency_check.platforms,
    we extend() the lists present in the base module before passing them to
    mdep_check() 
    """
    should_exit = mdep_check(dependency_set=GUI, exit_on_failure=False)
    
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk as gtk
        from gi.repository import GObject as gobject
        assert gtk.MAJOR_VERSION >= 3
    except Exception as e:
        msg = 'The GTK package requirements are not met, please make sure your'\
              ' system meets these requirements:\n'\
              '    - PyGTK >= 3.0\n'\
              '    - GTK >= 3.0\n'
        print(msg)
        should_exit = True

    if not which('dot'):
        msg = 'The required "dot" binary is missing, please install the' \
              ' "graphviz" package in your operating system.'
        print(msg)
        should_exit = True

    if should_exit:
        sys.exit(1)