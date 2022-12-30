# -*- coding: utf8 -*-

"""
html_export.py

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
import html

from w4af.core.data.parsers.doc.http_request_parser import http_request_parser
from w4af.core.data.misc.encoding import smart_unicode

def html_export(request_string):
    """
    :param request_string: The string of the request to export
    :return: A HTML that will perform the same HTTP request.
    """
    request_lines = request_string.split('\n\n')
    header = request_lines[0]
    body = '\n\n'.join(request_lines[1:])
    http_request = http_request_parser(header, body)
    res = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Exported HTTP Request from w4af</title>
    </head>
    <body>\n"""
    res += '<form action="' + html.escape(http_request.get_uri()
                                         .url_string, True)
    res += '" method="' + html.escape(http_request.get_method(), True) + '">\n'

    if http_request.get_data() and http_request.get_data() != '\n':
        post_data = http_request.get_raw_data()

        for token in post_data.iter_tokens():
            res += '<label>' + html.escape(smart_unicode(token.get_name())) + '</label>\n'
            res += '<input type="text" name="' + \
                html.escape(smart_unicode(token.get_name().strip()), True)
            res += '" value="' + html.escape(smart_unicode(token.get_value()), True) + '">\n'

    res += '<input type="submit">\n'
    res += '</form>\n'
    res += """</body>\n</html>"""

    return res
