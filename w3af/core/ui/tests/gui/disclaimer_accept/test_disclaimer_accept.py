"""
test_disclaimer_accept.py

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
import os
import subprocess

import pytest

from w4af.core.ui.tests.gui import GUI_TEST_ROOT_PATH
from w4af.core.ui.tests.wrappers.xpresser_unittest import XpresserUnittest
from w4af.core.data.db.startup_cfg import StartUpConfig


@pytest.mark.gui
class TestDisclaimer(XpresserUnittest):
    
    IMAGES = os.path.join(GUI_TEST_ROOT_PATH, 'disclaimer_accept', 'images')
    
    def start_gui(self):
        """
        Need to override this method in order to avoid waiting for the "real"
        UI to load.
        """
        self.gui_process = subprocess.Popen(["python", "w4af_gui", "-n"],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
        self.gui_process_pid = self.gui_process.pid

    def tearDown(self):
        XpresserUnittest.tearDown(self)
        
        # Just in case... we don't want to break other tests
        startup_cfg = StartUpConfig()
        startup_cfg.accepted_disclaimer = True
        startup_cfg.save()

    def test_disclaimer_shown_accept(self):
        startup_cfg = StartUpConfig()
        startup_cfg.accepted_disclaimer = False
        startup_cfg.save()
        
        self.find('accept_terms_conditions')
        self.click('simple_yes')
        
        self.find('owasp_top_10_profile')

    def test_disclaimer_shown_not_accept(self):
        startup_cfg = StartUpConfig()
        startup_cfg.accepted_disclaimer = False
        startup_cfg.save()
        
        self.find('accept_terms_conditions')
        self.click('simple_no')
        
        self.not_find('owasp_top_10_profile')

    def test_disclaimer_not_shown(self):
        startup_cfg = StartUpConfig()
        startup_cfg.accepted_disclaimer = True
        startup_cfg.save()
        
        self.not_find('accept_terms_conditions')
