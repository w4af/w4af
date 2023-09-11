"""
dependency_check.py

Copyright 2006 Andres Riancho

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
import sys
import warnings
import logging

from w4af.core.data.db.startup_cfg import StartUpConfig
from .utils import verify_python_version
verify_python_version()

import pkg_resources

from .helper_script import generate_helper_script
from .platforms.current_platform import get_current_platform
from .platforms.base_platform import CORE

def get_missing_os_packages(platform, dependency_set):
    """
    Check for missing operating system packages
    """
    missing_os_packages = []

    for os_package in platform.SYSTEM_PACKAGES[dependency_set]:
        if not platform.os_package_is_installed(os_package):
            missing_os_packages.append(os_package)

    return list(set(missing_os_packages))


def get_missing_external_commands(platform):
    """
    Check for missing external commands such as "retire" which is used
    by the retirejs grep plugin.

    :param platform: Current platform
    :return: A list with commands to be run to install the missing external commands
    """
    return platform.get_missing_external_commands()


def write_instructions_to_console(platform, os_packages, script_path,
                                  external_commands):
    #
    #    Report the missing system packages
    #
    msg = ('w4af\'s requirements are not met, one or more third-party'
           ' libraries need to be installed.\n\n')

    if os_packages:
        missing_pkgs = ' '.join(os_packages)

        msg += ('On %s systems please install the following operating'
                ' system packages before running the pip installer:\n'
                '    %s %s\n')
        print((msg % (platform.SYSTEM_NAME, platform.PKG_MANAGER_CMD,
                     missing_pkgs)))

    if external_commands:
        print('External programs used by w4af are not installed or were not found.'
              'Run these commands to install them on your system:\n')
        for cmd in external_commands:
            print(('    %s' % cmd))

        print('')

    platform.after_hook()

    msg = 'A script with these commands has been created for you at %s'
    print((msg % script_path))


def dependency_check(dependency_set=CORE, exit_on_failure=True, skip_external_commands=False):
    """
    This function verifies that the dependencies that are needed by the
    framework core are met.
    
    :return: True if the process should exit
    """
    if StartUpConfig().get_skip_dependencies_check():
        return False

    disable_warnings()

    platform = get_current_platform()

    os_packages = get_missing_os_packages(platform, dependency_set)
    if skip_external_commands:
        external_commands = []
    else:
        external_commands = get_missing_external_commands(platform)

    enable_warnings()

    # If everything is installed, just exit
    if not os_packages and not external_commands:
        # False means: do not exit()
        return False

    script_path = generate_helper_script(platform.PKG_MANAGER_CMD, os_packages,
                        external_commands)

    write_instructions_to_console(platform, os_packages, script_path,
                                  external_commands)
    
    if exit_on_failure:
        sys.exit(1)
    else:
        return True


def disable_warnings():
    # nltk raises a warning... which I want to ignore...
    warnings.filterwarnings('ignore', '.*',)

    # scapy raises an error if tcpdump is not found in PATH
    logging.disable(logging.CRITICAL)


def enable_warnings():
    # Enable warnings once again
    warnings.resetwarnings()
    
    # re-enable the logging module
    logging.disable(logging.NOTSET)
