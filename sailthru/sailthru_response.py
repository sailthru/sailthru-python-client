# -*- coding: utf-8 -*-

try: 
    import simplejson as json
except ImportError: 
    import json

class SailthruResponse(object):
    def __init__(self, response):
        self.response = response

    def is_ok(self):
        return (self.response.status_code == 200)

    def get_body(self, as_dictionary = True):
        content = self.response.content
        if as_dictionary == True:
            return json.loads(content)
        else:
            return content

    def get_response(self):
        return self.response

    def get_status_code(self):
        return self.response.status_code

class SailthruResponseError(object):
    def __init__(self, sailthru_response):
        self.response_dict = sailthru_response.get_body()

    def get_message(self):
        try:
            return self.response_dict['errormsg']
        except KeyError:
            return None

    def get_code(self):
        try:
            return self.response_dict['error']
        except KeyError:
            return None

