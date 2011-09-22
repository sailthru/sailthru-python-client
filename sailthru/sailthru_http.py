# -*- coding: utf-8 -*-

import requests
from sailthru_error import SailthruClientError
from sailthru_response import SailthruResponse

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
    try:
	headers = { 'User-Agent': 'Sailthru API Python Client' }
	response = requests.request(method, url, data, None, headers, None, file_data)
        return SailthruResponse(response)
	if (response.status_code == requests.codes.ok):
	    return response.content
	else:
	    response.raise_for_status()
	    return response
    except requests.HTTPError, e:
	raise SailthruClientError(str(e))
    except requests.RequestException, e:
	raise SailthruClientError(str(e))
