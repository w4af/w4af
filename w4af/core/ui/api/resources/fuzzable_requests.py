"""
fuzzable_requests.py

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
from flask import jsonify
from base64 import b64encode

import w4af.core.data.kb.knowledge_base as kb

from w4af.core.ui.api import app
from w4af.core.ui.api.utils.error import abort
from w4af.core.ui.api.utils.auth import requires_auth
from w4af.core.ui.api.utils.scans import get_scan_info_from_id
from w4af.core.data.misc.encoding import smart_str_ignore, smart_unicode


@app.route('/scans/<int:scan_id>/fuzzable-requests/', methods=['GET'])
@requires_auth
def get_fuzzable_request_list(scan_id):
    """
    A list with all the known fuzzable requests by this scanner

    :param scan_id: The scan ID
    :return: Fuzzable requests (serialized as base64 encoded string) in a list
    """
    scan_info = get_scan_info_from_id(scan_id)
    if scan_info is None:
        abort(404, 'Scan not found')

    data = []

    for fuzzable_request in kb.kb.get_all_known_fuzzable_requests():
        data.append(smart_unicode(b64encode(smart_str_ignore(fuzzable_request.dump()))))

    return jsonify({'items': data})
