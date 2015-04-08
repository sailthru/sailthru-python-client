# -*- coding: utf-8 -*-

import platform
import requests
from .sailthru_error import SailthruClientError
from .sailthru_response import SailthruResponse

def flatten_nested_hash(hash_table):
    """
    Flatten nested dictionary for GET / POST / DELETE API request
    """
    def flatten(hash_table, brackets=True):
        f = {}
        for key,value in hash_table.items():
            _key = '[' + str(key) + ']' if (brackets == True) else str(key)
            if type(value) is dict:
                for k,v in flatten(value).items():
                    f[_key + k] = v
            elif type(value) is list:
                temp_hash = {}
                for i,v in enumerate(value):
                    temp_hash[str(i)] = v
                for k,v in flatten(temp_hash).items():
                    f[ _key + k] = v
            else:
                f[_key] = value
        return f
    return flatten(hash_table, False)

def sailthru_http_request(url, data, method, file_data = None):
    """
    Perform an HTTP GET / POST / DELETE request
    """
    files = {}
    data = flatten_nested_hash(data)
    method = method.upper()
    params = data if method != 'POST' else None
    body = data if method == 'POST' else None
    try:
        headers = { 'User-Agent': 'Sailthru API Python Client %s; Python Version: %s' % ('2.2.0', platform.python_version())}
        response = requests.request(method, url, params = params, data = data, files = file_data, headers = headers, timeout = 10)
        if response.status_code is None:
            raise SailthruClientError(response.error)
        return SailthruResponse(response)
    except requests.HTTPError as e:
        raise SailthruClientError(str(e))
    except requests.RequestException as e:
        raise SailthruClientError(str(e))
