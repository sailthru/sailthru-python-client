sailthru-python-client
====================

Python binding for [Sailthru API](http://getstarted.sailthru.com/api) based on [Requests](https://github.com/kennethreitz/requests)

It will make request in `JSON` format.

Tested with `Python 2.7.x` but it should work with 2.6.x also.

### Installation (Tested with Python 2.7.x)

Installing with [pip](http://www.pip-installer.org/):

    pip install sailthru-client
    
### Running tests
    nosetests -v

Simple Example
--------
``` python
from sailthru.sailthru_client import SailthruClient
from sailthru.sailthru_response import SailthruResponseError
from sailthru.sailthru_error import SailthruClientError

api_key = '*******'
api_secret = '*******'
sailthru_client = SailthruClient(api_key, api_secret)

try:
    response = sailthru_client.api_get("email", {"email": "praj@sailthru.com"})

    if response.is_ok():
        body = response.get_body()
        print body
    else:
        error = response.get_error()
        print "Error: " + error.get_message()
        print "Status Code: " + str(response.get_status_code())
        print "Error Code: " + str(error.get_error_code())
except SailthruClientError, e:
    # Handle exceptions
    print "Exception"
    print e
```

### Making POST Request
``` python
request_data = {'email': 'praj@sailthru.com', 'verified': 1, 'vars': {'name': 'Prajwal Tuladhar', 'address': {'city': 'Jackson Heights', 'zip': 11372, 'state': 'NY'}}, 'twitter': 'infynyxx'}
response = sc.api_post('email', request_data)
```

### Making GET Request
``` python
request_data = {'email': 'praj@sailthru.com'}
response = sc.api_get('email', request_data)
```

### Making DELETE Request
``` python
request_data = {'template': 'My-unused template'}
response = sc.api_delete('template', request_data)
```

### Handling Postbacks
``` python
# for authenticating verify postbacks
verify_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'send_id': 'TE8EZ3-LmosnAgAA', 'sig': 'generated_signature'}
is_verified_postback = sailtrhu_client.recieve_verify_post(verify_params)

### Authenticating optout postbacks
optout_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
is_optout_postback = sailtrhu_client.recieve_optout_post(optout__params)

### Authenticating hardbounce postbacks
hardbounce_params = {'action': 'hardbounce', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
is_hardbounce_postback = sailtrhu_client.recieve_hardbounce_post(hardbounce_params)
```
    
### Multipart Request
``` python
# import job API call
response = sailthru_client.api_post("job", {"job": "import", "file": "file_location", "list": "Python-List"}, ['file'])
```
