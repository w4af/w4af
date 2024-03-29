"""
factory.py

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
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.dc.headers import Headers
from w4af.core.data.url.HTTPRequest import HTTPRequest


def create_fuzzable_request_from_request(request, add_headers=None):
    """
    :return: A fuzzable request with the same info as request
    """
    if not isinstance(request, HTTPRequest):
        raise TypeError('Requires HTTPRequest to create FuzzableRequest.')
    
    url = request.url_object
    post_data = str(request.data or '')
    method = request.get_method()

    headers = Headers(list(request.headers.items()))
    headers.update(list(request.unredirected_hdrs.items()))
    headers.update(add_headers or Headers())

    return FuzzableRequest.from_parts(url, method=method, post_data=post_data,
                                      headers=headers)



