# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse


def json_response(content, status_code=200, headers={}):
    """
    Simple function to serialise content and return a valid HTTP response.

    It takes three parameters:
        - content (required): the content to serialise.
        - status_code (default 200): The HTTP status code to use.
        - headers (default None): The headers to add to the response.
    """
    response = HttpResponse()
    response.write(json.dumps(content))
    response.status_code = status_code
    response['Content-Type'] = 'application/json; charset=utf-8'
    if headers:
        for key, value in headers.items:
            response[key] = value

    return response
