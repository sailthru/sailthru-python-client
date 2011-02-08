import hashlib
import urllib, urllib2

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

def extract_params(params):
    """
    Extracts the values of a set of parameters, recursing into nested dictionaries.
    """
    values = []
    for key, value in params.items():
        if type(value) == type(dict()):
            values.extend(extract_params(value))
        elif type(value) == type(list()):
            values.extend(value)
        else:
            values.append(value)
    return values

def get_signature_string(params, secret):
    """
    Returns the unhashed signature string (secret + sorted list of param values) for an API call.
    @param params: dictionary values to generate signature string
    @param sercret: secret string
    """
    str_list = []
    for item in extract_params(params):
        str_list.append(str(item))
    print str_list
    str_list.sort()
    print str_list
    print "".join(str_list)
    return secret + "".join(str_list)

def get_signature_hash(params, secret):
    """
    Returns an MD5 hash of the signature string for an API call.
    @param params: dictionary values to generate signature hash
    @param sercret: secret string
    """
    return hashlib.md5(get_signature_string(params, secret)).hexdigest()


class SailthruClient:

    """
    This class makes HTTP Request to Sailthru API server
    Response from server depends on the format being queried
    If 'json' format is requested, client will recieve JSON object
    XML format is also available but XML response have not been tested thoroughly
    https://github.com/sailthru/sailthru-python-client

    Usage:
        from sailthru import SailthruClient
        api_key = "your-api-key"
        api_secret = "api-secret"
        client = SailthruCLient(api_key, api_secret)
    """

    def __init__(self, api_key, secret, api_url=None):
        self.api_key = api_key
        self.secret = secret
        self.api_url = api_url if (api_url is not None) else 'https://api.sailthru.com'
        self.user_agent = 'Sailthru API Python Client'

    def send(self, template, email, _vars = {}, options = {}, schedule_time = None):
        """
        Remotely send an email template to a single email address.
        http://docs.sailthru.com/api/send
        @param template: template string
        @param email: Email value
        @param _vars: a key/value hash of the replacement vars to use in the send. Each var may be referenced as {varname} within the template itself
        @param options: optional dictionary to include replyto and/or test keys
        @param schedule_time: do not send the email immediately, but at some point in the future. Any date recognized by PHP's strtotime function is valid, but be sure to specify timezone or use a UTC time to avoid confusion
        """
        data = {}
        data['template'] = template
        data['email'] = email
        data['vars'] = _vars
        data['options'] = options
        if schedule_time is not None:
            data['schedule_time'] = schedule_time
        return self._api_post('send', data)

    def multi_send(self, template, emails, _vars = {}, evars = {}, options = {}):
        """
        Remotely send an email template to multiple email addresses.
        http://docs.sailthru.com/api/send
        @param template: template string
        @param emails: List with email values or comma separated email string
        @param _vars: a key/value hash of the replacement vars to use in the send. Each var may be referenced as {varname} within the template itself
        @param options: optional dictionary to include replyto and/or test keys
        @param schedule_time: do not send the email immediately, but at some point in the future. Any date recognized by PHP's strtotime function is valid, but be sure to specify timezone or use a UTC time to avoid confusion
        """
        data = {}
        data['template'] = template
        data['email'] = ','.join(emails) if type(emails) is list else emails
        data['vars'] = _vars
        data['evars'] = evars
        data['options'] = options
        return self._api_post('send', data)

    def get_send(self, send_id):
        """
        Get the status of a send
        """
        return self._api_get('send', {'send_id': send_id})

    def cancel_send(self, send_id):
        """
        Cancels an email that you had previously scheduled for future sending with the schedule_time parameter. It is not possible to cancel an email that has not been scheduled.
        """
        return self._api_delete('send', {'send_id': send_id})

    def get_email(self, email):
        """
        get user email data
        """
        data = {'email': email}
        return self._api_request('email', data, 'GET')

    def _api_get(self, action, data):
        """
        Perform an HTTP GET request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'GET')

    def _api_post(self, action, data):
        """
        Perform an HTTP POST request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'POST')

    def _api_delete(self, action, data):
        """
        Perform an HTTP DELETE request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'DELETE')

    def _api_request(self, action, data, request_type):
        """
        Make Request to Sailthru API with given data and api key, format and signature hash
        """
        data['api_key'] = self.api_key
        data['format'] = data.get('format', 'json')
        data['sig'] = get_signature_hash(data, self.secret)
        return self._http_request(self.api_url+'/'+action, data, request_type)

    def _http_request(self, url, data, method='POST'):
        """
        Perform an HTTP GET / POST / DELETE request
        """
        data = flatten_nested_hash(data)
        data = urllib.urlencode(data, True)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        try:
            if method == 'POST':
                req = urllib2.Request(url, data)
            else:
                url += '?' + data
                req = urllib2.Request(url)
            req.add_header('User-Agent', self.user_agent)
            req.get_method = lambda: method
            response = opener.open(req)
            response_data = response.read()
            response.close()
            return response_data
        except urllib2.URLError, e:
            return str(e)
        except urllib2.HTTPError, e:
            return e.read()