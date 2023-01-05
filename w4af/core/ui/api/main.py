"""
main.py

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
import socket
import argparse
import os

from w4af.core.ui.api import app
from w4af.core.ui.api.utils.cli import process_cmd_args_config

from w4af.core.ui.api.utils.digital_certificate import SSLCertificate


def main(launch_gui=False):
    """
    Entry point for the REST API
    :return: Zero if everything went well
    """
    try:
        args = process_cmd_args_config(app)
    except argparse.ArgumentTypeError as ate:
        print(('%s' % ate))
        return 1

    # And finally start the app:
    proto = "http"
    static = None
    if launch_gui:
        if not args.disable_ssl:
            proto = "https"
        import threading
        import webbrowser
        threading.Timer(1.25,
           lambda: webbrowser.open(
                f"{proto}://{app.config['HOST']}:{app.config['PORT']}"
                + "/static/index.html")
                ).start()
        static = {
            '/static': os.path.join(os.path.dirname(__file__), 'static')
        }
    try:
        if args.disable_ssl:
            app.run(host=app.config['HOST'], port=app.config['PORT'],
                    debug=args.verbose, use_reloader=False, threaded=True,
                    static_files=static)
        else:
            proto = "https"
            cert_key = SSLCertificate().get_cert_key(app.config['HOST'])

            app.run(host=app.config['HOST'], port=app.config['PORT'],
                    debug=args.verbose, use_reloader=False, threaded=True,
                    ssl_context=cert_key, static_files=static)
    except socket.error as se:
        print(('Failed to start REST API server: %s' % se.strerror))
        return 1
    
    return 0
