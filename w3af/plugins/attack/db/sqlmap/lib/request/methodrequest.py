#!/usr/bin/env python

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import urllib.request, urllib.error, urllib.parse

class MethodRequest(urllib.request.Request):
    """
    Used to create HEAD/PUT/DELETE/... requests with urllib2
    """

    def set_method(self, method):
        self.method = method.upper()

    def get_method(self):
        return getattr(self, 'method', urllib.request.Request.get_method(self))
