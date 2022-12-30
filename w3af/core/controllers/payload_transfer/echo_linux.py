"""
EchoLinux.py

Copyright 2006 Andres Riancho

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
import time

import w4af.core.controllers.output_manager as om

from w4af.core.controllers.payload_transfer.base_payload_transfer import BasePayloadTransfer
from w4af.core.data.misc.encoding import smart_str


class EchoLinux(BasePayloadTransfer):
    """
    This is a class that defines how to send a file to a remote server using
    the "echo" command.
    """

    def __init__(self, exec_method, os):
        super(EchoLinux, self).__init__(exec_method, os)
        self._exec_method = exec_method
        self._os = os
        self._step = 300

    def can_transfer(self):
        """
        This method is used to test if the transfer method works as expected.
        The implementation of this should transfer 10 bytes and check if they
        arrived as expected to the other end.
        """
        # Check if echo exists and works as expected
        res = smart_str(self._exec_method("/bin/echo -n 'w4af'"))
        if b'w4af' != res.strip():
            om.out.debug('Remote server returned: "' + str(res) +
                         '" when expecting "w4af".')
            return False
        else:
            return True

    def estimate_transfer_time(self, size):
        """
        :return: An estimated transfer time for a file with the specified size.
        """
        before = time.time()
        res = self._exec_method("echo w4af")
        after = time.time()

        # Estimate the time...
        numberOfRequests = size / self._step
        requestTime = after - before
        timeTaken = round(requestTime * numberOfRequests)

        om.out.debug(
            'The file transfer will take "' + str(timeTaken) + '" seconds.')
        return int(timeTaken)

    def transfer(self, data_str, destination):
        """
        This method is used to transfer the data_str from w4af to the compromised server.
        """
        self._filename = destination

        # Zeroing destination file
        self._exec_method('> ' + self._filename)

        i = 0
        error_count = 1
        success_count = 1
        while i < len(data_str) and (error_count < 20 or (success_count / error_count > 0.25)):
            # Prepare the command
            cmd = "/bin/echo -ne "
            for c in data_str[i:i + self._step]:
                cmd += '\\\\' + oct(ord(c)).replace('0o', '0').zfill(4)

            cmd += " >> " + self._filename + " && /bin/echo -n 1"

            # Send the command to the remote server
            res = self._exec_method(cmd)

            # None result means the request failed
            if res != b'1':
                success_count += 1
                i += self._step
            else:
                om.out.debug("Error transferring bytes %d to %d... will retry" % (i, i + self._step))
                error_count += 1

        return self.verify_upload(data_str, self._filename)

    def get_speed(self):
        """
        :return: The transfer speed of the transfer object. It should return
                 a number between 100 (fast) and 1 (slow)
        """
        return 1
