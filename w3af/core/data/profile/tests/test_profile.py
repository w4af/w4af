# -*- coding: UTF-8 -*-
"""
test_profile.py

Copyright 2015 Andres Riancho

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
import unittest
import shutil
import os

from w4af.core.data.profile.profile import profile


class TestProfiles(unittest.TestCase):

    def test_load_profile_using_name_in_file(self):
        p = profile('OWASP_TOP10', workdir='.')
        target_tmp = '/tmp/OWASP_TOP10.pw4af'

        shutil.copy(p.profile_file_name, '/tmp/')
        with open(target_tmp) as f:
            profile_content = f.read()
        profile_content = profile_content.replace('name = OWASP_TOP10',
                                                  'name = foobar')
        with open(target_tmp, "w") as f:
            f.write(profile_content)

        p = profile('foobar', workdir='/tmp/')
        self.assertEqual(target_tmp, p.profile_file_name)

        os.unlink(target_tmp)

    def test_remove_profile_using_name_in_file(self):
        p = profile('OWASP_TOP10', workdir='.')
        target_tmp = '/tmp/OWASP_TOP10.pw4af'

        shutil.copy(p.profile_file_name, '/tmp/')
        with open(target_tmp) as f:
            profile_content = f.read()
        profile_content = profile_content.replace('name = OWASP_TOP10',
                                                  'name = foobar')
        with open(target_tmp, "w") as f:
            f.write(profile_content)

        p = profile('foobar', workdir='/tmp/')
        p.remove()

        self.assertFalse(os.path.exists(target_tmp))

