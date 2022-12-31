"""
splash.py

Copyright 2007 Andres Riancho

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
import os

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

from w4af.core.ui.gui.constants import w4af_ICON
from w4af.core.controllers.dependency_check.platforms.mac import MacOSX
from w4af import ROOT_PATH


class Splash(gtk.Window):
    """Builds the Splash window.

    :author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    """
    def __init__(self):
        super(Splash, self).__init__()

        # These two lines are required here to make sure that unity shows the
        # correct information in the menu
        self.set_icon_from_file(w4af_ICON)
        self.set_title('w4af - 0wn the Web')

        vbox = gtk.VBox()
        self.add(vbox)

        # content
        splash = os.path.join(ROOT_PATH, 'core', 'ui', 'gui', 'data', 'splash.png')
        img = gtk.Image.new_from_file(splash)
        vbox.pack_start(img, False, False, 0)
        self.label = gtk.Label()
        vbox.pack_start(self.label, False, False, 0)

        # Splash screen doesn't have decoration (at least where supported)
        # https://github.com/andresriancho/w4af/issues/9084
        if not MacOSX.is_current_platform():
            self.set_decorated(False)

        # color and position
        color = gdk.color_parse('#f2f2ff')
        self.modify_bg(gtk.StateFlags.NORMAL, color)
        self.set_position(gtk.WindowPosition.CENTER)
        self.set_size_request(644, 315)

        # ensure it is rendered immediately
        self.show_all()

        while gtk.events_pending():
            gtk.main_iteration()

    def push(self, text):
        """New text to be shown in the Splash."""
        self.label.set_text(text)
        while gtk.events_pending():
            gtk.main_iteration()
