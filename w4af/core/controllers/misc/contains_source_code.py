"""
is_source_file.py

Copyright 2010 Andres Riancho

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
import re
import string

from w4af.core.data.quick_match.multi_re import MultiRE
from w4af.core.data.misc.encoding import DEFAULT_ENCODING

PHP = 'PHP'
ASP = 'ASP'
JSP = 'JSP'
ASPX = 'ASPX'
UNKNOWN = 'Unknown'
SHELL = 'Shell script'
JAVA = 'Java'
RUBY = 'Ruby'
PYTHON = 'Python'
GROOVY = 'Groovy'


SOURCE_CODE = (
    (br'<\?php .*?\?>', {PHP}),
    (br'<\?php\n.*?\?>', {PHP}),       # These two are required for perf #2129
    (br'<\?php\r.*?\?>', {PHP}),       # and are repeated over the list

    # Need to review how to re-add these in the future
    # https://github.com/andresriancho/w3af/issues/2129
    #
    #('<\? .*?\?>', {PHP}),
    #('<\?\n.*?\?>', {PHP}),
    #('<\?\r.*?\?>', {PHP}),

    (br'<% .*?%>', {ASP, JSP}),
    (br'<%\n.*?%>', {ASP, JSP}),
    (br'<%\r.*?%>', {ASP, JSP}),

    (br'<%@ .*?%>', {ASPX}),          # http://goo.gl/zEjHA4
    (br'<%@\n.*?%>', {ASPX}),
    (br'<%@\r.*?%>', {ASPX}),

    (br'<asp:.*?%>', {ASPX}),
    (br'<jsp:.*?>', {JSP}),

    (br'<%! .*%>', {JSP}),
    (br'<%!\n.*%>', {JSP}),
    (br'<%!\r.*%>', {JSP}),
    (br'<%=.*%>', {JSP, PHP, RUBY}),

    (br'<!--\s*%.*?%(--)?>', {PHP}),
    (br'<!--\s*\?.*?\?(--)?>', {ASP, JSP}),
    (br'<!--\s*jsp:.*?(--)?>', {JSP}),

    (br'#include <', {UNKNOWN}),

    (br'#!/usr/', {SHELL}),
    (br'#!/opt/', {SHELL}),
    (br'#!/bin/', {SHELL}),

    (br'(^|\W)import java\.', {JAVA}),
    (br'(^|\W)public class \w{1,60}\s?\{\s.*\Wpublic', {JAVA}),
    (br'(^|\W)package\s\w+\;', {JAVA}),

    (br'<!--g:render', {GROOVY}),

    # Python
    (br'(^|\W)def .*?\(.*?\):(\n|\r)', {PYTHON}),

    # Ruby
    (br'(^|\W)class \w{1,60}\s*<?\s*[a-zA-Z0-9_:]{0,90}.*?\W(def|validates)\s.*?\send($|\W)', {RUBY}),
)

BLACKLIST = {b'xml', b'xpacket'}

_multi_re = MultiRE(SOURCE_CODE, re.IGNORECASE | re.DOTALL)

def contains_source_code(http_response):
    """
    :param http_response: The HTTP response object
    :return: A tuple with:
                - re.match object if the file_content matches a source code file
                - A tuple containing the programming language names
    """
    body = http_response.get_body()
    if isinstance(body, str):
        body = body.encode(DEFAULT_ENCODING)

    for match, _, _, lang in _multi_re.query(body):

        if is_false_positive(http_response, match, lang):
            continue

        return match, lang

    return None, None


def is_false_positive(http_response, match, detected_langs):
    """
    :param http_response: The HTTP response object
    :param match: The regular expression match object
    :param detected_langs: Language names
    :return: True if this match is a false positive and should be ignored
    """
    match_str = match.group(0)

    for blacklist_str in BLACKLIST:
        if blacklist_str in match_str:
            return True

    # Avoid some (rather common) false positives that appear in JS files
    # https://github.com/andresriancho/w3af/issues/5379
    # https://github.com/andresriancho/w3af/issues/12379
    #
    # The detection for some languages is weaker, thus we don't fully trust
    # them:
    for lang in detected_langs:
        if lang in {PHP, ASP, JSP, ASPX}:
            if 'javascript' in http_response.content_type:
                return True

    # Avoid some false positives in large binary files where we might
    # have <% , then 182837 binary chars, and finally %>.
    printable = 0.0
    ratio = 0.9

    for char in match_str:
        if char in string.printable.encode(DEFAULT_ENCODING):
            printable += 1

    if (printable / len(match_str)) < ratio:
        return True

    return False
