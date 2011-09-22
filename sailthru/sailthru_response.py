# -*- coding: utf-8 -*-

import ast

class SailthruResponse:
    def __init__(self, response):
        self.response = response

    def is_ok(self):
        return (self.response.status_code == 200)

    def get_body(self, as_dictionary = True):
        content = self.response.content
        return ast.literal_eval(content) if as_dictionary == True else content

    def get_response(self):
        return self.response

    def get_status_code(self):
        return self.response.status_code

class SailthruResponseError:
    def __init__(self, sailthru_response):
        self.response_dict = ast.literal_eval(sailthru_response.get_body())

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

