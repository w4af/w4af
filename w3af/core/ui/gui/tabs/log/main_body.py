"""
main_body.py

Copyright 2007 Andres Riancho

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


from w4af.core.ui.gui.entries import RememberingVPaned, RememberingHPaned
from w4af.core.ui.gui.tabs.log.messages import Messages
from w4af.core.ui.gui.tabs.log.graph import LogGraph
from w4af.core.ui.gui.tabs.log.stats import StatsViewer


class LogBody(RememberingVPaned):
    """Body of the log tab.

    :param w4af: the Core instance.

    :author: Facundo Batista <facundobatista =at= taniquetil.com.ar>
    """
    def __init__(self, w4af):
        super(LogBody, self).__init__(w4af, "pane-logbody")
        self.w4af = w4af

        # stats and graph hbox
        bottom_hbox = RememberingHPaned(w4af, "pane-logbody-stats-graph")

        # bottom widget
        # The log and status visualization
        graph = LogGraph(w4af)
        stats = StatsViewer(w4af)
        
        bottom_hbox.pack1(stats)
        bottom_hbox.pack2(graph)
        bottom_hbox.show_all()
        
        messag = Messages()
        messag.show()
        
        # Add to the main vpan
        self.pack1(messag)
        self.pack2(bottom_hbox)

        self.show()

