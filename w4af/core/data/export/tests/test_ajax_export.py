"""
test_ajax_export.py

Copyright 2012 Andres Riancho

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
import unittest

from w4af.core.data.export.ajax_export import ajax_export

EXPECTED_SIMPLE = """/* Init AJAX stuff */

var xmlhttp = false;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
// JScript gives us Conditional compilation, we can cope with old IE versions.
// and security blocked creation of the objects.
try {
    xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
} catch (e) {
    try {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (E) {
        xmlhttp = false;
    }
}
@end @*/

if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
    try {
        xmlhttp = new XMLHttpRequest();
    } catch (e) {
        xmlhttp = false;
    }
}
if (!xmlhttp && window.createRequest) {
    try {
        xmlhttp = window.createRequest();
    } catch (e) {
        xmlhttp = false;
    }
}
/* Finished AJAX initialization */

/* Create the request, please remember the same-origin policy, which might
affect how and if this request is sent by the browser */
xmlhttp.open("GET", "http://www.w4af.net/", true);

/* Debugging code, this should be removed for real life XSS exploits */
xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 ) {
        alert(xmlhttp.responseText);
    }
}


/* Add headers to the request and send it, please note that custom headers
might be removed by the browser and/or generate an exception that will
make the request fail */
xmlhttp.setRequestHeaders("Host", "www.w4af.net");
xmlhttp.setRequestHeaders("Foo", "bar");
xmlhttp.send(null);
"""

EXPECTED_POST = """/* Init AJAX stuff */

var xmlhttp = false;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
// JScript gives us Conditional compilation, we can cope with old IE versions.
// and security blocked creation of the objects.
try {
    xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
} catch (e) {
    try {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (E) {
        xmlhttp = false;
    }
}
@end @*/

if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
    try {
        xmlhttp = new XMLHttpRequest();
    } catch (e) {
        xmlhttp = false;
    }
}
if (!xmlhttp && window.createRequest) {
    try {
        xmlhttp = window.createRequest();
    } catch (e) {
        xmlhttp = false;
    }
}
/* Finished AJAX initialization */

/* Create the request, please remember the same-origin policy, which might
affect how and if this request is sent by the browser */
xmlhttp.open("POST", "http://www.w4af.net/", true);

/* Debugging code, this should be removed for real life XSS exploits */
xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 ) {
        alert(xmlhttp.responseText);
    }
}


/* Add headers to the request and send it, please note that custom headers
might be removed by the browser and/or generate an exception that will
make the request fail */
xmlhttp.setRequestHeaders("Host", "www.w4af.net");
xmlhttp.setRequestHeaders("Content-Type", "application/x-www-form-urlencoded");
var post_data = (<r><![CDATA[a=1]]></r>).toString();
xmlhttp.send(post_data);
"""


class TestAjaxExport(unittest.TestCase):

    def test_export_GET(self):
        http_request = 'GET http://www.w4af.net/ HTTP/1.1\n' \
                       'Host: www.w4af.net\n' \
                       'Foo: bar\n' \
                       '\n'
        ajax_code = ajax_export(http_request)

        self.assertEqual(ajax_code, EXPECTED_SIMPLE)

    def test_export_POST(self):
        http_request = 'POST http://www.w4af.net/ HTTP/1.1\n' \
                       'Host: www.w4af.net\n' \
                       'Content-Length: 3\n' \
                       'Content-Type: application/x-www-form-urlencoded\n' \
                       '\n' \
                       'a=1'
        ajax_code = ajax_export(http_request)

        self.assertEqual(ajax_code, EXPECTED_POST)
