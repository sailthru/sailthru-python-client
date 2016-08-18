# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json

class SailthruResponse(object):
    def __init__(self, response):
        self.response = response
        self.json_error = None

        try:
            self.json = json.loads(response.content)
        except ValueError as e:
            self.json = None
            self.json_error = str(e)

    def is_ok(self):
        return self.json and not set(["error", "errormsg"]) == set(self.json)

    def get_body(self, as_dictionary=True):
        if as_dictionary:
            return self.json
        else:
            return self.response.content

    def get_response(self):
        return self.response

    def get_status_code(self):
        return self.response.status_code

    def get_error(self):
        if self.is_ok():
            return False

        if self.json_error is None:
            code = self.json["error"]
            msg = self.json["errormsg"]
        else:
            code = 0
            msg = self.json_error

        return SailthruResponseError(msg, code)

    def get_rate_limit_headers(self):
        headers = self.response.headers

        if all(k in headers for k in ('X-Rate-Limit-Limit', 'X-Rate-Limit-Remaining', 'X-Rate-Limit-Reset')):
            return { 'limit' : int(headers['X-Rate-Limit-Limit']),
                     'remaining' : int(headers['X-Rate-Limit-Remaining']),
                     'reset' : int(headers['X-Rate-Limit-Reset']) }

        return None

class SailthruResponseError(object):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def get_message(self):
        return self.message

    def get_error_code(self):
        return self.code
