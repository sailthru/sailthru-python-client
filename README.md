sailthru-python-client
====================

A simple client library to remotely access the `Sailthru REST API` as per [http://docs.sailthru.com/api](http://docs.sailthru.com/api).

By default, it will make request in `JSON` format.

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

Examples
--------
    from sailthru import sailthru_client as sc
    
    api_key = '*******'
    api_secret = '*******'
    sailthru_client = sc.SailthruClient(api_key, api_secret)
    try:
        response = sailthru_client.get_email('eli@sailthru.com')
    except urllib2.URLError as e:
        # handle exceptions
        print e
    except urllib2.HTTPError as e:
        # handle exceptions
        print e

### postbacks
    
    # for authenticating verify postbacks
    verify_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'send_id': 'TE8EZ3-LmosnAgAA', 'sig': 'generated_signature'}
    is_verified_postback = sailtrhu_client.recieve_verify_post(verify_params)

    # for authenticating optout postbacks
    optout_params = {'action': 'verify', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
    is_optout_postback = sailtrhu_client.recieve_optout_post(optout__params)

    # for authenticating hardbounce postbacks
    hardbounce_params = {'action': 'hardbounce', 'email': 'praj@sailthru.com', 'sig': 'generated_signature'}
    is_hardbounce_postback = sailtrhu_client.recieve_hardbounce_post(hardbounce_params)
