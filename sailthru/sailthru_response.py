# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json

class SailthruResponse(object):
    def __init__(self, response):
        self.response = response
        self.json_error = False

        try:
            self.json = json.loads(response.content)
        except ValueError as e:
            self.json = None
            self.json_error = str(e)

    def is_ok(self):
        return self.json_error is not None and self.json and not "error" in self.json.keys()

    def get_body(self, as_dictionary = True):
        if as_dictionary is True:
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

        if self.json_error is not False:
            code = 0
            msg = self.json_error
        else:
            code = self.json["error"]
            msg = self.json["errormsg"]

        return SailthruResponseError(msg, code)

class SailthruResponseError(object):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def get_message(self):
       return self.message

    def get_error_code(self):
        return self.code
