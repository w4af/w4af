"""
random_user_agent.py

Copyright 2012 Andres Riancho

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
import random
import os

from w4af import ROOT_PATH

UA_CACHE = []
UA_FILE = os.path.join(ROOT_PATH, 'core', 'data', 'user_agent',
                       'user-agent-list.txt')


def get_random_user_agent(agent_list=UA_CACHE):
    if not len(agent_list):
        with open(UA_FILE) as f:

            for line in f:
                line = line.strip()

                if line:
                    agent_list.append(line)

    ua = random.choice(UA_CACHE)
    return ua
