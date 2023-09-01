"""
scans.py

Copyright 2015 Andres Riancho

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

from uuid import uuid4
from tempfile import tempdir

from w4af.core.ui.api.db.master import SCANS
import w4af.core.controllers.output_manager as om

import re


def validate_profile_file(profile_name):
    pattern = r'^\w+\.pw4af$'
    return bool(re.match(pattern, profile_name))


def validate_file_exist(profile_name):
    cwd = os.getcwd()
    file_string = f"{cwd}/profiles/{profile_name}"
    return os.path.exists(file_string)


def get_scan_info_from_id(scan_id):
    return SCANS.get(scan_id, None)


def get_new_scan_id():
    return len(list(SCANS.keys()))


def create_temp_profile(scan_profile):
    """
    Writes the scan_profile to a file

    :param scan_profile: The contents of a profile configuration
    :return: The scan profile file name and the directory where it was created
    """
    scan_profile_file = os.path.join(tempdir, '%s.pw4af' % uuid4())
    with open(scan_profile_file, 'w') as profile_fh:
        profile_fh.write(scan_profile)

    

    print("***************create_temp_profile*********************")
    print(scan_profile_file)
    print(tempdir)
    print("***************create_temp_profile*********************")

    return scan_profile_file, tempdir


def remove_temp_profile(scan_profile_file_name):
    """
    Remove temp profile after using
    :param scan_profile_file_name: path to the temp profile
    :return: None
    """
    try:
        os.remove(scan_profile_file_name)
    except OSError:
        pass


def start_scan_helper(scan_info):
    """
    Start scan from scan_info

    :param scan_info: ScanInfo object contains initialized w4afCore
    """
    w4af_core = scan_info.w4af_core
    try:
        # Init plugins!
        w4af_core.plugins.init_plugins()

        # Clear all current output plugins
        # Add the REST API output plugin
        om.manager.set_output_plugins([])
        om.manager.set_output_plugin_inst(scan_info.output)

        # Start the scan!
        w4af_core.verify_environment()
        w4af_core.start()
    except Exception as e:
        scan_info.exception = e
        try:
            w4af_core.stop()
        except AttributeError:
            # Reduce some exceptions found during interpreter shutdown
            pass

    finally:
        scan_info.finished = True

        try:
            os.unlink(scan_info.profile_path)
        except (AttributeError, IOError) as _:
            # Reduce some exceptions found during interpreter shutdown
            pass

