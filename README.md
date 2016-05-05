sailthru-python-client
======================


For installation instructions, documentation, and examples please visit:
[http://getstarted.sailthru.com/new-for-developers-overview/api-client-library/python](http://getstarted.sailthru.com/new-for-developers-overview/api-client-library/python)

A simple client library to remotely access the `Sailthru REST API` as per [http://getstarted.sailthru.com/api](http://getstarted.sailthru.com/developers/api)

Python binding for [Sailthru API](http://getstarted.sailthru.com/api) based on [Requests](http://docs.python-requests.org/en/latest/)

It will make requests in `JSON` format.

Supports Python 2.6, 2.7, 3.3+

### Installation (Tested with Python 2.7.x)

Installing with [pip](http://www.pip-installer.org/):

    pip install sailthru-client
    
### Running tests
Install tox and then type:

    tox

### API Rate Limiting

Here is an example how to check rate limiting and throttle API calls based on that. For more information about Rate Limiting, see [Sailthru Documentation](https://getstarted.sailthru.com/new-for-developers-overview/api/api-technical-details/#Rate_Limiting)


```python
sailthru_client = SailthruClient(api_key, api_secret)

# ... make some api calls ...

rate_limit_info = sailthru_client.get_last_rate_limit_info('user', 'POST')

# get_last_rate_limit_info returns None if given endpoint/method wasn't triggered previously
if rate_limit_info is not None:
    limit = rate_limit_info['limit'];
    remaining = rate_limit_info['remaining'];
    reset_timestamp = rate_limit_info['reset'];

    # throttle api calls based on last rate limit info
    if remaining <= 0:
         seconds_till_reset = reset_timestamp - time.time()
         # sleep or perform other business logic before next user api call
         time.sleep(seconds_till_reset);
```