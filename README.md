sailthru-python-client
======================


For installation instructions, documentation, and examples please visit:
[http://getstarted.sailthru.com/new-for-developers-overview/api-client-library/python](http://getstarted.sailthru.com/new-for-developers-overview/api-client-library/python)

A simple client library to remotely access the `Sailthru REST API` as per [http://getstarted.sailthru.com/api](http://getstarted.sailthru.com/developers/api)

Python binding for [Sailthru API](http://getstarted.sailthru.com/api) based on [Requests](http://docs.python-requests.org/en/latest/)

It will make requests in `JSON` format.

CI discovers every stable Python release line from 3.11 through the latest release.
These are tested compatibility targets; other runtimes are outside CI coverage.

### Installation

Installing with [pip](http://www.pip-installer.org/):

    pip install sailthru-client
    
### Running tests

```bash
python -m pip install 'tox>=4.11,<5'
python -m tox -e py
```

This runs unit tests and installs the built wheel and source distribution into
separate temporary consumers for local requests with dummy credentials. It does
not publish. To retain the validated artifacts, use `python -m tox -e py -- --outdir dist`.

CI runs on PRs, pushes to `master`, weekly, and manual runs.

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
