"""
helpers.py

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
import os
import sys
import copy
import pprint
import tempfile
import io
import distro

from itertools import chain

from w4af.core.controllers.misc.get_w4af_version import get_w4af_version
from w4af.core.data.fuzzer.utils import rand_alnum


def pprint_plugins(w4af_core):
    # Return a pretty-printed string from the plugins dicts
    plugs_opts = copy.deepcopy(w4af_core.plugins.get_all_plugin_options())
    plugs = w4af_core.plugins.get_all_enabled_plugins()

    for ptype, plugin_list in plugs.items():
        for plugin in plugin_list:
            if plugin not in chain(*(list(pt.keys()) for pt in plugs_opts.values())):
                plugs_opts[ptype][plugin] = {}

    if not any(plugs_opts.values()):
        # No plugins configured, we return an empty string so the users of
        # this function understand that there is no config
        return ''

    plugins = io.StringIO()
    pprint.pprint(plugs_opts, plugins)
    return plugins.getvalue()


def gettempdir():
    return tempfile.gettempdir()


def get_platform_dist():
    """
    :return: A human readable representation of platform.dist() , unknown if
             the module returned none / ''
    """
    if distro.id() == '' and distro.version() == '' and distro.name() == '':
        return 'Unknown'

    return '%s %s %s' % (distro.id(), distro.name(), distro.version())


def get_versions():
    try:
        from gi.repository import gtk
    except ImportError:
        gtk_version = 'No GTK module installed'
    else:
        gtk_version = '%s.x' % (gtk.MAJOR_VERSION)

    # String containing the versions for python, gtk and pygtk
    versions = ('  Python version: %s\n'
                '  Platform: %s\n'
                '  GTK version: %s\n'
                '  w4af version:\n    %s')
    
    w4af_version = '\n    '.join(get_w4af_version().split('\n'))
    
    versions = versions % (sys.version.replace('\n', ''),
                           get_platform_dist(),
                           gtk_version,
                           w4af_version)
        
    return versions


def create_crash_file(exception):
    filename = 'w4af-crash-%s.txt' % rand_alnum(5)
    filename = os.path.join(gettempdir(), filename)
    with open(filename, 'w') as crash_dump:
        crash_dump.write(_('Submit this bug here:'
                        ' https://github.com/codders/w4af/issues/new \n'))
        crash_dump.write(get_versions())
        crash_dump.write(exception)
    return filename
