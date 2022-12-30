"""
ssl_daemon.py

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
import socketserver
import threading
import socket
import time
import ssl
import os

from .upper_daemon import UpperDaemon, UpperTCPHandler

HTTP_RESPONSE = b"HTTP/1.1 200 Ok\r\n"\
                b"Connection: close\r\n"\
                b"Content-Type: text/html\r\n"\
                b"Content-Length: 3\r\n\r\nabc"


class RawSSLDaemon(UpperDaemon):
    """
    Echo the data sent by the client, but upper case it first. SSL version of
    UpperDaemon.
    """
    def __init__(self, handler=UpperTCPHandler, ssl_version=ssl.PROTOCOL_TLS):
        super(RawSSLDaemon, self).__init__(handler=handler)
        self.ssl_version = ssl_version

    def run(self):
        self.server = socketserver.TCPServer(self.server_address, self.handler,
                                             bind_and_activate=False)

        key_file = os.path.join(os.path.dirname(__file__), 'unittest.key')
        cert_file = os.path.join(os.path.dirname(__file__), 'unittest.crt')

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)

        with context.wrap_socket(self.server.socket, server_side=True) as ssl_sock:
            self.server.socket = ssl_sock

            self.server.server_bind()
            self.server.server_activate()
            self.server.serve_forever()


class SSLServer(threading.Thread):

    def __init__(self, listen, port, certfile, proto=ssl.PROTOCOL_TLS_SERVER,
                 http_response=HTTP_RESPONSE):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = 'SSLServer'
        
        self.listen = listen
        self.port = port
        self.cert = certfile
        self.proto = proto
        self.http_response = http_response

        self.sock = socket.socket()
        self.sock.bind((listen, port))
        self.sock.listen(5)

        self.errors = []
        self.context = ssl.SSLContext(self.proto)
        self.context.load_cert_chain(self.cert)
        self.context.verify_mode = ssl.CERT_NONE

    def accept(self):
        self.sock = self.context.wrap_socket(self.sock,
                                                server_side=True,
                                                do_handshake_on_connect=False,
                                                suppress_ragged_eofs=True)

        newsocket, fromaddr = self.sock.accept()

        try:
            # pylint: disable=E1101
            newsocket.do_handshake()
            # pylint: enable=E1101
        except:
            # The ssl certificate might request a connection with
            # SSL protocol v2 and that will "break" the handshake
            newsocket.close()

        #print 'Connection from %s port %s, sending HTTP response' % fromaddr
        try:
            newsocket.send(self.http_response)
        except Exception as e:
            self.errors.append(e)
            #print 'Failed to send HTTP response to client: "%s"' % e
        finally:
            # without this sleep, the socket closes before the response is
            # sent, which creates an RemoteDisconnected error in the tests
            # (at least in test_bad_file_descriptor_8125_local). Maybe
            # send here is non-blocking??
            time.sleep(0.5)
            newsocket.close()
            #print 'Closed connection from %s port %s' % fromaddr

    def run(self):
        self.should_stop = False
        while not self.should_stop:
            self.accept()

    def stop(self):
        self.should_stop = True
        try:
            self.sock.close()

            # Connection to force stop,
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.listen, self.port))
            s.close()
        except:
            pass

    def wait_for_start(self):
        while self.get_port() is None:
            time.sleep(0.5)

    def get_port(self):
        try:
            return self.sock.getsockname()[1]
        except:
            return None