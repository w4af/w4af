"""
message_consumer.py

Copyright 2013 Andres Riancho

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
from gi.repository import GObject as gobject
import queue

from w4af.core.ui.gui.output.gtk_output import subscribe_to_messages
from w4af.core.ui.gui.output.gtk_output import Message


class MessageConsumer(object):
    """Defines a base message consumer

    :author: Andres Riancho <andres.riancho@gmail.com>
    """
    def __init__(self):
        super(MessageConsumer, self).__init__()

        # get the messages
        subscribe_to_messages(self._message_observer)
        self.messages = queue.Queue()
        gobject.idle_add(self._process_queue().__next__)
        
    def _message_observer(self, message):
        self.messages.put(message)

    def _process_queue(self):
        """Sends a message to the handle_message method.

        The message is read from the iterated queue.

        @returns: True to gobject to keep calling it, and False when all
                  it's done.
        """
        while True:
            yield True
            
            try:
                # Sleeping here prevents the GUI from running at 100% cpu
                msg = self.messages.get(timeout=0.01)
            except queue.Empty:
                continue
            else:
                if msg is None:
                    continue
                
                # Given that in some cases the handle_message takes some
                # time to run, we've implemented this loop to give the method
                # the opportunity to give the control back to the mainloop
                for _ in self.handle_message(msg):
                    yield True

    def handle_message(self, msg):
        """
        :param msg: A gtk_output.Message object.
        """
        if not isinstance(msg, Message):
            raise TypeError('Expected Message and got %s instead.' % type(msg))
        
        yield True
