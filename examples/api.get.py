# -*- coding: utf-8 -*-

from sailthru.sailthru_client import SailthruClient
from sailthru.sailthru_response import SailthruResponseError
from sailthru.sailthru_error import SailthruClientError

api_key = 'API_KEY'
api_secret = 'SUPER_SECRET'
sailthru_client = SailthruClient(api_key, api_secret)

try:
    response = sailthru_client.api_get("user", {"id": "praj@sailthru.com"})

    if response.is_ok():
        body = response.get_body()
        # handle body which is of type dictionary
        print (body)
    else:
        error = response.get_error()
        print ("Error: " + error.get_message())
        print ("Status Code: " + str(response.get_status_code()))
        print ("Error Code: " + str(error.get_error_code()))
except SailthruClientError as e:
    # Handle exceptions
    print ("Exception")
    print (e)
