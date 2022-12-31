"""
test_git_client.py

Copyright 2013 Andres Riancho

This file is part of w4af, http://w4af.net/ .

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
import subprocess
import pytest

from unittest.mock import MagicMock

from w4af.core.controllers.misc.home_dir import w4af_LOCAL_PATH
from w4af.core.controllers.auto_update.git_client import GitClient
from w4af.core.controllers.auto_update.utils import get_current_branch

@pytest.mark.git
class TestGitClient(unittest.TestCase):
    
    def test_get_URL(self):
        client = GitClient(w4af_LOCAL_PATH)
        
        # https://github.com/andresriancho/w4af/ provides a list of all the
        # URLs which can be used to clone the repo
        REPO_URLS = ('git@github.com:codders/w4af-python3.git',
                     'https://github.com/codders/w4af-python3.git',
                     'git://github.com/codders/w4af-python3.git')
        
        self.assertIn(client.URL, REPO_URLS)
    
    def test_get_local_head_id(self):
        client = GitClient(w4af_LOCAL_PATH)
        local_head = client.get_local_head_id()
        
        self.assertEqual(len(local_head), 40)
        self.assertIsInstance(local_head, str)
        
        # Get the ID using an alternative way for double checking
        proc = subprocess.Popen(['git', 'log', '-n', '1'], stdout=subprocess.PIPE)
        commit_id_line = proc.stdout.readline()
        commit_id_line = commit_id_line.strip()
        _, commit_id = commit_id_line.split(' ')              
        
        self.assertEqual(local_head, commit_id)
        
    def test_get_remote_head_id(self):
        # For some strange reason jenkins creates a branch called
        # jenkins-<job name> during the build, which makes this test FAIL
        # if we don't take that into account
        if get_current_branch().startswith('jenkins-'):
            pytest.skip('Workaround for Jenkins Git plugin wierdness.')
        
        client = GitClient(w4af_LOCAL_PATH)
        # I don't really want to wait for the local repo to update itself
        # using "git fetch", so I simply put this as a mock
        client.fetch = MagicMock()
        
        remote_head = client.get_remote_head_id()
        client.fetch.assert_called_once_with()
                
        self.assertEqual(len(remote_head), 40)
        self.assertIsInstance(remote_head, str)
        
        # Get the ID using an alternative way for double checking
        branch = 'refs/remotes/origin/%s' % get_current_branch()
        proc = subprocess.Popen(['git', 'for-each-ref', branch], stdout=subprocess.PIPE)
        commit_id_line = proc.stdout.readline()
        commit_id_line = commit_id_line.strip()
        commit_id, _ = commit_id_line.split(' ')
        
        self.assertEqual(remote_head, commit_id)
        
