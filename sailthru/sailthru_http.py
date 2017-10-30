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
        for key, value in hash_table.items():
            _key = '[' + str(key) + ']' if brackets else str(key)
            if isinstance(value, dict):
                for k, v in flatten(value).items():
                    f[_key + k] = v
            elif isinstance(value, list):
                temp_hash = {}
                for i, v in enumerate(value):
                    temp_hash[str(i)] = v
                for k, v in flatten(temp_hash).items():
                    f[_key + k] = v
            else:
                f[_key] = value
        return f
    return flatten(hash_table, False)

def sailthru_http_request(url, data, method, file_data=None,
                          timeout=10, retries=0):
    """
    Perform an HTTP GET / POST / DELETE request
    """
    data = flatten_nested_hash(data)
    method = method.upper()
    params, data = (None, data) if method == 'POST' else (data, None)

    try:
        headers = {'User-Agent': 'Sailthru API Python Client %s; Python Version: %s' % ('2.3.3', platform.python_version())}
        if retries > 0:
            session = requests.Session()
            # We retry on connection errors and all 5xx errors.  We do
            # not retry on read errors since for POST requests that
            # happens after the POST has finished, and POSTs are not
            # necessarily safe to re-do.
            retry = requests.urllib3.Retry(retries,
                                           read=0,
                                           method_whitelist=False,
                                           status_forcelist={500, 502, 503, 504},
                                           raise_on_status=False)
            session.mount(url, requests.adapters.HTTPAdapter(max_retries=retry))
        else:
            session = requests
        response = session.request(method, url,
                                   params=params,
                                   data=data,
                                   files=file_data,
                                   headers=headers,
                                   timeout=timeout)
        return SailthruResponse(response)
    except requests.HTTPError as e:
        raise SailthruClientError(str(e))
    except requests.RequestException as e:
        raise SailthruClientError(str(e))
