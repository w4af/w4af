"""
test_latest_vulndb.py

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
import pkg_resources
from pypi_simple import PyPISimple

MESSAGE = ('There is a new vulndb available at pypi! These are the steps'
           ' to follow in order to upgrade:\n\n'
           ' 1- Update requirements.py file\n'
           ' 2- Update vulns.py to point to the new DB entries\n'
           ' 3- Ask packagers (Kali) to update the dependency in their repos\n'
           ' 4- Update the w4af-kali repository to require new package\n')


class TestLatestVulnDB(unittest.TestCase):
    def test_latest_vulndb(self):
        pkg = 'vulndb'
        found = None
        with PyPISimple() as client:
            requests_page = client.get_project_page('vulndb')
        latest_package_online = requests_page.packages[0]
        local_package = pkg_resources.get_distribution('vulndb')

        if pkg_resources.parse_version(local_package.version) < pkg_resources.parse_version(latest_package_online.version):
            found = True

        if found:
            self.assertTrue(False, MESSAGE)
