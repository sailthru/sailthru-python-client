# -*- coding: utf-8 -*-

import hashlib
import urllib, urllib2
import string

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
    str_list.sort()
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
        http://docs.sailthru.com/api/email
        """
        data = {'email': email}
        return self._api_request('email', data, 'GET')

    def set_email(self, email, _vars={}, lists=[], templates=[], verified=0, optout=None, send=None, send_vars=[]):
        """
        Update information about one of your users, including adding and removing the user from lists.
        http://docs.sailthru.com/api/email
        """
        data = {}
        data['email'] = email
        data['vars'] = _vars
        data['lists'] = lists
        data['templates'] = templates
        data['verified'] = int(verified)
        if optout is not None:
            data['optout'] = optout
        if send is not None:
            data['send'] = send
        data['send_vars'] = send_vars
        return self._api_post('email', data)

    def schedule_blast(self, name, list, schedule_time, from_name, from_email, subject, content_html, content_text, options={}):
        """
        Schedule a mass mail blast
        http://docs.sailthru.com/api/blast
        @param name: name to give to this new blast
        @param list: mailing list name to send to
        @param schedule_time:  when the blast should send. Dates in the past will be scheduled for immediate delivery. Any English textual datetime format known to PHP's strtotime function is acceptable, such as 2009-03-18 23:57:22 UTC, now (immediate delivery), +3 hours (3 hours from now), or February 14, 9:30 EST. Be sure to specify a timezone if you use an exact time.
        @param from_name: name appearing in the "From" of the email
        @param from_email: email address to use as the "from" – choose from any of your verified emails
        @param subject: subject line of the email
        @param content_html: HTML format version of the email
        @param content_text: Text format version of the email
        @param options: optional parameters dictionary
            blast_id
            copy_blast
            copy_template
            replyto
            report_email
            is_link_tracking
            is_google_analytics
            is_public
            suppress_list
            test_vars
            email_hour_range
            abtest
            test_percent
            data_feed_url
        """
        data = options
        data['name'] = name
        data['list'] = list
        data['schedule_time'] = schedule_time
        data['from_name'] = from_name
        data['from_email'] = from_email
        data['subject'] = subject
        data['content_html'] = content_html
        data['content_text'] = content_text
        return self._api_post('blast', data)

    def update_blast(self, blast_id, name=None, list=None, schedule_time=None, from_name=None, from_email=None, subject=None, content_html=None, content_text=None, options={}):
        """
        updates existing blast
        http://docs.sailthru.com/api/blast
        @param blast_id: blast id
        @param name: name of the blast
        @param list: blast list
        @param schedule_time: new schedule time
        @param from_name: name appearing in the "From" of the email
        @param from_email: email address to use as the "from" – choose from any of your verified emails
        @param subject: subject line of the email
        @param content_html: HTML format version of the email
        @param content_text: Text format version of the email
        @param options: optional parameters dictionary
            blast_id
            copy_blast
            copy_template
            replyto
            report_email
            is_link_tracking
            is_google_analytics
            is_public
            suppress_list
            test_vars
            email_hour_range
            abtest
            test_percent
            data_feed_url
        """
        data = options
        data['blast_id'] = blast_id
        if name is not None:
            data['name'] = name
        if list is not None:
            data['list'] = list
        if schedule_time is not None:
            data['schedule_time'] = schedule_time
        if from_name is not None:
            data['from_name'] = from_name
        if from_email is not None:
            data['from_email'] = from_email
        if subject is not None:
            data['subject'] = subject
        if content_html is not None:
            data['content_html'] = content_html
        if content_text is not None:
            data['content_text'] = content_text
        return self._api_post('blast', data)

    def get_blast(self, blast_id):
        """
        Get Blast information
        http://docs.sailthru.com/api/blast
        """
        return self._api_get('blast', {'blast_id': blast_id})

    def delete_blast(self, blast_id):
        """
        delete existing blast
        """
        return self._api_delete('blast', {'blast_id': blast_id})

    def cancel_blast(self, blast_id):
        """
        Cancel a scheduled Blast
        """
        data = {}
        data['blast_id'] = blast_id
        data['schedule_time'] = ''
        return self._api_post('blast', data)

    def get_template(self, template_name):
        """
        get information of a given template
        """
        return self._api_get('template', {'template': template_name})

    def get_templates(self):
        """
        get metadata for all user templates
        """
        data = {'template': ''}
        return self._api_get('template', data)

    def save_template(self, template, template_fields = {}):
        data = template_fields
        data['template'] = template
        return self._api_post('template', data)

    def get_list(self, list, format='txt'):
        """
        Download a list. Obviously, this can potentially be a very large download.
        'txt' is default format since, its more compact as compare to others
        http://docs.sailthru.com/api/list
        """
        data = {}
        data['list'] = list
        data['format'] = format
        return self._api_get('list', data)

    def get_lists(self):
        """
        Get metadata for all lists
        """
        data = {'list': ''} #blank list
        return self._api_get('list', data)

    def save_list(self, list, emails):
        """
        Upload a list. The list import job is queued and will happen shortly after the API request.
        http://docs.sailthru.com/api/list
        @param list: list name
        @param emails: List of email values or comma separated string
        """
        data = {}
        data['list'] = list
        data['emails'] = ','.join(emails) if emails is list else emails
        return self._api_post('list', data)

    def delete_list(self, list):
        """
        delete given list
        http://docs.sailthru.com/api/list
        """
        return self._api_delete('list', {'list': list})

    def import_contacts(self, email, password, include_name=False):
        """
        Fetch email contacts from a user's address book on one of the major email websites. Currently supports AOL, Gmail, Hotmail, and Yahoo! Mail.
        """
        data = {}
        data['email'] = email
        data['password'] = password
        if include_name == True:
            data['names'] = 1
        return self._api_post('contacts', data)

    def push_content(self, title, url, date=None, tags=None, vars={}):
        """
        Push a new piece of content to Sailthru, triggering any applicable alerts.
        @param title: title string for the content
        @param url: URL string for the content
        @param date: date string
        @param tags: list or comma separated string values
        @param vars: replaceable vars dictionary
        """
        data = {}
        data['title'] = title
        data['url'] = url
        if date is not None:
            data['date'] = date
        if tags is not None:
            data['tags'] = ",".join(tags) if type(tags) is list else tags
        if len(vars) > 0:
            data['vars'] = vars
        return self._api_post('content', data)

    def get_alert(self, email):
        """
        Retrieve a user's alert settings.
        """
        return self._api_get('alert', {'email': email})

    def save_alert(self, email, type, template, when=None, options={}):
        """
        Add a new alert to a user. You can add either a realtime or a summary alert (daily/weekly).
        http://docs.sailthru.com/api/alert

        Usage:
            email = 'praj@sailthru.com'
            type = 'weekly'
            template = 'default'
            when = '+5 hours'
            alert_options = {'match': {}, 'min': {}, 'max': {}, 'tags': []}
            alert_options['match']['type'] = 'shoes'
            alert_options['min']['price'] = 20000 #cents
            alert_options['tags'] = ['red', 'blue', 'green']
            response = client.save_alert(email, type, template, when, alert_options)

        @param email: Email value
        @param type: daily|weekly|realtime
        @param template: template name
        @param when: date string required for summary alert (daily/weekly)
        @param options: dictionary value for adding tags, max price, min price, match type
        """
        data = options
        data['email'] = email
        data['type'] = type
        data['template'] = template
        if (type == 'weekly' or type == 'daily'):
            data['when'] = when
        return self._api_post('alert', data)

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