"""
helper_script.py

Copyright 2013 Andres Riancho

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
import tempfile

from .utils import running_in_virtualenv


SCRIPT_NAME = 'w4af_dependency_install.sh'


def generate_helper_script(pkg_manager_cmd, os_packages, external_commands):
    """
    Generates a helper script to be run by the user to install all the
    dependencies.
    
    :return: The path to the script name.
    """
    temp_dir = tempfile.gettempdir()
    
    script_path = os.path.join(temp_dir, SCRIPT_NAME)
    
    script_file = open(script_path, 'w')
    script_file.write('#!/bin/bash\n')
    
    #
    #    Report the missing system packages
    #
    if os_packages:
        missing_pkgs = ' '.join(os_packages)
        script_file.write('%s %s\n' % (pkg_manager_cmd, missing_pkgs))

    for cmd in external_commands:
        script_file.write('%s\n' % cmd)

    # Make it executable
    os.chmod(script_path, 0o755)

    script_file.close()
    return script_path
