"""
read_decorator.py

Copyright 2009 Andres Riancho

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
from functools import wraps

import w4af.core.controllers.output_manager as om
from w4af.core.data.misc.encoding import smart_str_ignore, smart_unicode


def read_debug(fn):
    
    @wraps(fn)
    def new(self, filename):
        #   Run the original function
        result = fn(self, filename)
        no_newline_result = smart_str_ignore(result).replace(b'\n', b'')
        no_newline_result = no_newline_result.replace(b'\r', b'')

        #   Format the message
        if len(no_newline_result) > 25:
            file_content = '"' + smart_unicode(no_newline_result[:25]) + '...' + '"'
        else:
            file_content = '"' + smart_unicode(no_newline_result[:25]) + '"'

        msg = 'read( "' + filename + '" , ' + file_content + \
            ') == ' + str(len(file_content)) + ' bytes.'

        #   Print the message to the debug output
        om.out.debug(msg)

        #   Return the result
        return result

    return new
