# -*- coding: utf-8 -*-
"""
Custom exceptions, mostly used for easier error handling.
"""


class RESTError(Exception):
    """Exception raised for REST errors that need to be communicated to the
    user.

    Attributes:
        status_code -- The status code to return.
        content -- The serialisable content to return.
    """
    def __init__(self, status_code, content):
        super(RESTError, self).__init__()
        self.status_code, self.content = status_code, content
