# -*- coding: utf-8 -*-

import hashlib
from sailthru_http import sailthru_http_request

try:
    import simplejson as json
except ImportError:
    import json

def extract_params(params):
    """
    Extracts the values of a set of parameters, recursing into nested dictionaries.
    """
    values = []
    if type(params) == type(dict()):
        for key, value in params.items():
            values.extend(extract_params(value))
    elif type(params) == type(list()):
        for value in params:
            values.extend(extract_params(value))
    else:
        values.append(params)
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


class SailthruClient(object):

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

    def send(self, template, email, _vars=None, options=None, schedule_time=None, limit=None):
        """
        Remotely send an email template to a single email address.
        http://docs.sailthru.com/api/send
        @param template: template string
        @param email: Email value
        @param _vars: a key/value hash of the replacement vars to use in the send. Each var may be referenced as {varname} within the template itself
        @param options: optional dictionary to include replyto and/or test keys
        @param limit: optional dictionary to name, time, and handle conflicts of limits
        @param schedule_time: do not send the email immediately, but at some point in the future. Any date recognized by PHP's strtotime function is valid, but be sure to specify timezone or use a UTC time to avoid confusion
        """
        _vars = _vars or {}
        options = options or {}
        limit = limit or {}
        data = {}
        data['template'] = template
        data['email'] = email
        data['vars'] = _vars
        data['options'] = options.copy()
        data['limit'] = limit.copy()
        if schedule_time is not None:
            data['schedule_time'] = schedule_time
        return self.api_post('send', data)

    def multi_send(self, template, emails, _vars=None, evars=None, options=None):
        """
        Remotely send an email template to multiple email addresses.
        http://docs.sailthru.com/api/send
        @param template: template string
        @param emails: List with email values or comma separated email string
        @param _vars: a key/value hash of the replacement vars to use in the send. Each var may be referenced as {varname} within the template itself
        @param options: optional dictionary to include replyto and/or test keys
        @param schedule_time: do not send the email immediately, but at some point in the future. Any date recognized by PHP's strtotime function is valid, but be sure to specify timezone or use a UTC time to avoid confusion
        """
        _vars = _vars or {}
        evars = evars or {}
        options = options or {}
        data = {}
        data['template'] = template
        data['email'] = ','.join(emails) if type(emails) is list else emails
        data['vars'] = _vars.copy()
        data['evars'] = evars.copy()
        data['options'] = options.copy()
        return self.api_post('send', data)

    def get_send(self, send_id):
        """
        Get the status of a send
        """
        return self.api_get('send', {'send_id': send_id})

    def cancel_send(self, send_id):
        """
        Cancels an email that you had previously scheduled for future sending with the schedule_time parameter. It is not possible to cancel an email that has not been scheduled.
        """
        return self.api_delete('send', {'send_id': send_id})

    def get_email(self, email):
        """
        get user email data
        http://docs.sailthru.com/api/email
        """
        data = {'email': email}
        return self._api_request('email', data, 'GET')

    def set_email(self, email, _vars=None, lists=None, templates=None, verified=0, optout=None, send=None, send_vars=None):
        """
        Update information about one of your users, including adding and removing the user from lists.
        http://docs.sailthru.com/api/email
        """
        _vars = _vars or {}
        lists = lists or []
        templates = templates or []
        send_vars = send_vars or []
        data = {}
        data['email'] = email
        data['vars'] = _vars.copy()
        data['lists'] = lists
        data['templates'] = templates
        data['verified'] = int(verified)
        if optout is not None:
            data['optout'] = optout
        if send is not None:
            data['send'] = send
        data['send_vars'] = send_vars
        return self.api_post('email', data)

    def get_user(self, idvalue, options=None):
        """
        get user by a given id
        http://getstarted.sailthru.com/api/user
        """
        options = options or {}
        data = options.copy()
        data['id'] = idvalue
        return self.api_get('user', data)

    def save_user(self, idvalue, options=None):
        """
        save user by a given id
        http://getstarted.sailthru.com/api/user
        """
        options = options or {}
        data = options.copy()
        data['id'] = idvalue
        return self.api_post('user', data)

    def schedule_blast(self, name, list, schedule_time, from_name, from_email, subject, content_html, content_text, options=None):
        """
        Schedule a mass mail blast
        http://docs.sailthru.com/api/blast
        @param name: name to give to this new blast
        @param list: mailing list name to send to
        @param schedule_time:  when the blast should send. Dates in the past will be scheduled for immediate delivery. Any English textual datetime format known to PHP's strtotime function is acceptable, such as 2009-03-18 23:57:22 UTC, now (immediate delivery), +3 hours (3 hours from now), or February 14, 9:30 EST. Be sure to specify a timezone if you use an exact time.
        @param from_name: name appearing in the "From" of the email
        @param from_email: email address to use as the "from" - choose from any of your verified emails
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
        options = options or {}
        data = options.copy()
        data['name'] = name
        data['list'] = list
        data['schedule_time'] = schedule_time
        data['from_name'] = from_name
        data['from_email'] = from_email
        data['subject'] = subject
        data['content_html'] = content_html
        data['content_text'] = content_text
        return self.api_post('blast', data)

    def schedule_blast_from_template(self, template, list, schedule_time, options=None):
        """
        Schedule a mass mail blast from template
        http://docs.sailthru.com/api/blast
        @param template: template to copy from
        @param list: List String
        @param schedule_time
        @param options: additional optional params
        """
        options = options or {}
        data = options.copy()
        data['copy_template'] = template
        data['list'] = list
        data['schedule_time'] = schedule_time
        return self.api_post('blast', data)

    def schedule_blast_from_blast(self, blast_id, schedule_time, options=None):
        """
        Schedule a mass mail blast from previous blast
        http://docs.sailthru.com/api/blast
        @param blast_id: blast_id to copy from
        @param schedule_time
        @param options: additional optional params
        """
        options = options or {}
        data = options.copy()
        data['copy_blast'] = blast_id
        data['schedule_time'] = schedule_time
        return self.api_post('blast', data)

    def update_blast(self, blast_id, name=None, list=None, schedule_time=None, from_name=None, from_email=None, subject=None, content_html=None, content_text=None, options=None):
        """
        updates existing blast
        http://docs.sailthru.com/api/blast
        @param blast_id: blast id
        @param name: name of the blast
        @param list: blast list
        @param schedule_time: new schedule time
        @param from_name: name appearing in the "From" of the email
        @param from_email: email address to use as the "from" - choose from any of your verified emails
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
        options = options or {}
        data = options.copy()
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
        return self.api_post('blast', data)

    def get_blast(self, blast_id):
        """
        Get Blast information
        http://docs.sailthru.com/api/blast
        """
        return self.api_get('blast', {'blast_id': blast_id})

    def delete_blast(self, blast_id):
        """
        delete existing blast
        """
        return self.api_delete('blast', {'blast_id': blast_id})

    def cancel_blast(self, blast_id):
        """
        Cancel a scheduled Blast
        """
        data = {}
        data['blast_id'] = blast_id
        data['schedule_time'] = ''
        return self.api_post('blast', data)

    def get_template(self, template_name):
        """
        get information of a given template
        """
        return self.api_get('template', {'template': template_name})

    def get_templates(self):
        """
        get metadata for all user templates
        """
        return self.api_get('template', {})

    def delete_template(self, template_name):
        """
        delete existing template
        """
        data = {'template': template_name}
        return self.api_delete('template', data)

    def save_template(self, template, template_fields=None):
        template_fields = template_fields or {}
        data = template_fields.copy()
        data['template'] = template
        return self.api_post('template', data)

    def get_list(self, list_name, options=None):
        """
        Get detailed metadata information about a list.
        """
        options = options or {}
        data = {'list': list_name}
        data.update(options)
        return self.api_get('list', data)

    def get_lists(self):
        """
        Get metadata for all lists
        """
        data = {'list': ''} #blank list
        return self.api_get('list', data)

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
        return self.api_post('list', data)

    def delete_list(self, list):
        """
        delete given list
        http://docs.sailthru.com/api/list
        """
        return self.api_delete('list', {'list': list})

    def import_contacts(self, email, password, include_name=False):
        """
        Fetch email contacts from a user's address book on one of the major email websites. Currently supports AOL, Gmail, Hotmail, and Yahoo! Mail.
        """
        data = {}
        data['email'] = email
        data['password'] = password
        if include_name == True:
            data['names'] = 1
        return self.api_post('contacts', data)

    def push_content(self, title, url, date=None, tags=None, vars=None):
        """
        Push a new piece of content to Sailthru, triggering any applicable alerts.
        @param title: title string for the content
        @param url: URL string for the content
        @param date: date string
        @param tags: list or comma separated string values
        @param vars: replaceable vars dictionary
        """
        vars = vars or {}
        data = {}
        data['title'] = title
        data['url'] = url
        if date is not None:
            data['date'] = date
        if tags is not None:
            data['tags'] = ",".join(tags) if type(tags) is list else tags
        if len(vars) > 0:
            data['vars'] = vars.copy()
        return self.api_post('content', data)

    def get_alert(self, email):
        """
        Retrieve a user's alert settings.
        """
        return self.api_get('alert', {'email': email})

    def save_alert(self, email, type, template, when=None, options=None):
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
        options = options or {}
        data = options.copy()
        data['email'] = email
        data['type'] = type
        data['template'] = template
        if (type == 'weekly' or type == 'daily'):
            data['when'] = when
        return self.api_post('alert', data)

    def delete_alert(self, email, alert_id):
        """
        delete user alert
        """
        data = {}
        data['email'] = email
        data['alert_id'] = alert_id
        return self.api_delete('alert', data)

    def purchase(self, email, items=None, incomplete=None, message_id=None, options=None):
        """
        Record that a user has made a purchase, or has added items to their purchase total.
        http://docs.sailthru.com/api/purchase
        @param email: Email string
        @param items: list of item dictionary with keys: id, title, price, qty, and url
        @param message_id: message_id string
        @param options
        """
        items = items or {}
        options = options or {}
        data = options.copy()
        data['email'] = email
        data['items'] = items
        if incomplete is not None:
            data['incomplete'] = incomplete
        if message_id is not None:
            data['message_id'] = message_id

        return self.api_post('purchase', data)

    def stats_list(self, list=None, date=None):
        """
        Retrieve information about your subscriber counts on a particular list, on a particular day.
        http://docs.sailthru.com/api/stat
        """
        data = {}
        if list is not None:
            data['list'] = list
        if date is not None:
            data['date'] = date
        data['stat'] = 'list'
        return self._stats(data)

    def stats_blast(self, blast_id=None, start_date=None, end_date=None, options=None):
        """
        Retrieve information about a particular blast or aggregated information from all of blasts over a specified date range.
        http://docs.sailthru.com/api/stat
        """
        options = options or {}
        data = options.copy()
        if blast_id is not None:
            data['blast_id'] = blast_id
        if start_date is not None:
            data['start_date'] = start_date
        if end_date is not None:
            data['end_date'] = end_date
        data['stat'] = 'blast'
        return self._stats(data)

    def _stats(self, data):
        """
        Make Stats API Request
        """
        return self.api_get('stats', data)

    def receive_verify_post(self, post_params):
        """
        Returns true if the incoming request is an authenticated verify post.
        """
        if type(post_params) is dict:
            required_params = ['action', 'email', 'send_id', 'sig']
            if self.check_for_valid_postback_actions(required_params, post_params) is False:
                return False
        else:
            return False

        if post_params['action'] != 'verify':
            return False

        sig = post_params['sig']
        post_params = post_params.copy()
        del post_params['sig']

        if sig != get_signature_hash(post_params, self.secret):
            return False

        send_response = self.get_send(post_params['send_id'])

        try:
            send_body = send_response.get_body()
            send_json = json.loads(send_body)
            if not 'email' in send_body:
                return False
            if send_json['email'] != post_params['email']:
                return False

            send_body = json.JSONEncoder().encode(send_body)

        except json.decoder.JSONDecodeError:
            return False

        return True

    def receive_optout_post(self, post_params):
        """
        Optout postbacks
        """
        if type(post_params) is dict:
            required_params = ['action', 'email', 'sig']
            if self.check_for_valid_postback_actions(required_params, post_params) is False:
                return False
        else:
            return False

        if post_params['action'] != 'optout':
            return False

        signature = post_params['sig']
        post_params = post_params.copy()
        del post_params['sig']

        if signature != get_signature_hash(post_params, self.secret):
            return False

        return True

    def receive_hardbounce_post(self, post_params):
        """
        Hard bounce postbacks
        """
        if type(post_params) is dict:
            required_params = ['action', 'email', 'sig']
            if self.check_for_valid_postback_actions(required_params, post_params ) is False:
                return False
        else:
            return False

        if post_params['action'] != 'hardbounce':
            return False

        signature = post_params['sig']
        post_params = post_params.copy()
        del post_params['sig']

        if signature != get_signature_hash(post_params, self.secret):
            return False

        # for sends
        if 'send_id' in post_params:
            send_id = post_params['send_id']
            send_response = self.get_send(send_id)
            try:
                send_response = send_response.get_body()
                send_response = json.JSONEncoder().encode(send_response)
                if not 'email' in send_response:
                    return False
            except json.decoder.JSONDecodeError as json_err:
                return False

        # for blasts
        if 'blast_id' in post_params:
            blast_id = post_params['blast_id']
            blast_response = self.get_blast(blast_id)
            try:
                blast_response = blast_response.get_body()
                blast_response = json.JSONEncoder().encode(blast_response)
                if 'error' in blast_response:
                    return False
            except json.decoder.JSONDecodeError:
                return False

        return True

    def check_for_valid_postback_actions(self, required_keys, post_params):
        """
        checks if post_params contain required keys
        """
        for key in required_keys:
            if not key in post_params:
                return False
        return True

    def api_get(self, action, data):
        """
        Perform an HTTP GET request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'GET')

    def api_post(self, action, data, binary_data_param=None):
        """
        Perform an HTTP POST request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        binary_data_param = binary_data_param or []
        if len(binary_data_param) > 0:
            return self.api_post_multipart(action, data, binary_data_param)
        else:
            return self._api_request(action, data, 'POST')

    def api_post_multipart(self, action, data, binary_data_param):
        """
         Perform an HTTP Multipart POST request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        @param: binary_data_params: array of multipart keys
        """
        binary_data = {}
        data_keys = data.keys()
        for param in binary_data_param:
            if param in data_keys:
                binary_data[param] = open(data[param], 'r')
                data = data.copy()
                del data[param]
        json_payload = self._prepare_json_payload(data)

        return self._http_request(self.api_url+'/'+action, json_payload, "POST", binary_data)

    def api_delete(self, action, data):
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
        return self._http_request(self.api_url+'/'+action, self._prepare_json_payload(data), request_type)

    def _http_request(self, url, data, method, file_data=None):
        file_data = file_data or {}
        return sailthru_http_request(url, data, method, file_data)

    def _prepare_json_payload(self, data):
        payload = {}
        payload['api_key'] = self.api_key
        payload['format'] = 'json'
        payload['json'] = json.dumps(data)
        signature = get_signature_hash(payload, self.secret)
        payload['sig'] = signature
        return payload
