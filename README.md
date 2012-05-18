sailthru-python-client
====================

A simple client library to remotely access the `Sailthru REST API` as per [http://docs.sailthru.com/api](http://docs.sailthru.com/api).

It will make request in `JSON` format.

Tested with `Python 2.6.x` but should work also with `>= 2.4.x`

It can make requests to following [API calls](http://docs.sailthru.com/api):

* [email](http://docs.sailthru.com/api/email)
* [send](http://docs.sailthru.com/api/send)
* [blast](http://docs.sailthru.com/api/blast)
* [template](http://docs.sailthru.com/api/template)
* [list](http://docs.sailthru.com/api/list)
* [contacts](http://docs.sailthru.com/api/contacts)
* [content](http://docs.sailthru.com/api/content)
* [alert](http://docs.sailthru.com/api/alert)
* [stats](http://docs.sailthru.com/api/stats)
* [purchase](http://docs.sailthru.com/api/purchase)
* [horizon](http://docs.sailthru.com/api/horizon)

For usage examples, you can take a look at [Ruby](https://github.com/sailthru/sailthru-ruby-client/blob/master/README.md) and [PHP](https://github.com/sailthru/sailthru-php5-client/blob/master/README.md) examples

### Installation (Tested with Python 2.7.x)
    pip install git+https://github.com/sailthru/sailthru-python-client.git#egg=sailthru-client
    
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
        sailthru_client = SailthruClient(api_key, secret)
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

### postbacks
    ``` python
    # for authenticating verify postbacks
    verify_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'send_id': 'TE8EZ3-LmosnAgAA', 'sig': 'generated_signature'}
    is_verified_postback = sailtrhu_client.recieve_verify_post(verify_params)

    # for authenticating optout postbacks
    optout_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
    is_optout_postback = sailtrhu_client.recieve_optout_post(optout__params)

    # for authenticating hardbounce postbacks
    hardbounce_params = {'action': 'hardbounce', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
    is_hardbounce_postback = sailtrhu_client.recieve_hardbounce_post(hardbounce_params)
    ```
    
## multipart POST
    ``` python
    response = sailthru_client.api_post("job", {"job": "import", "file": "file_location", "list": "Python-List"}, ['file'])
    ```
