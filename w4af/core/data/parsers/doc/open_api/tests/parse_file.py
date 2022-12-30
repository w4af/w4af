import os
import sys
import pprint

sys.path.append(os.getcwd())

from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.parsers.doc.open_api import OpenAPI
from w4af.core.data.url.HTTPResponse import HTTPResponse

spec_filename = sys.argv[1]

_, extension = os.path.splitext(spec_filename)

with open(spec_filename) as f:
    body = f.read()
headers = Headers(list({'Content-Type': 'application/%s' % extension}.items()))
response = HTTPResponse(200, body, headers,
                        URL('http://moth/swagger.%s' % extension),
                        URL('http://moth/swagger.%s' % extension),
                        _id=1)


parser = OpenAPI(response)
parser.parse()
api_calls = parser.get_api_calls()

for api_call in api_calls:
    method = api_call.get_method()
    headers = api_call.get_headers()
    data = api_call.get_data()

    uri = api_call.get_uri().url_string

    data = (method, uri, headers, data)

    pprint.pprint(data)
