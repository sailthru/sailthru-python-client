# -*- coding: utf-8 -*-

import hashlib
from .sailthru_http import sailthru_http_request

try:
    import simplejson as json
except ImportError:
    import json

def extract_params(params):
    """
    Extracts the values of a set of parameters, recursing into nested dictionaries.
    """
    values = []
    if isinstance(params, dict):
        for key, value in params.items():
            values.extend(extract_params(value))
    elif isinstance(params, list):
        for value in params:
            values.extend(extract_params(value))
    else:
        values.append(params)
    return values

def get_signature_string(params, secret):
    """
    Returns the unhashed signature string (secret + sorted list of param values) for an API call.
    @param params: dictionary values to generate signature string
    @param secret: secret string
    """
    str_list = [str(item) for item in extract_params(params)]
    str_list.sort()
    return (secret + ''.join(str_list)).encode('utf-8')

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

    Usage:
        from sailthru import SailthruClient
        api_key = "your-api-key"
        api_secret = "api-secret"
        client = SailthruClient(api_key, api_secret)
    """

    def __init__(self, api_key, secret, api_url=None):
        self.api_key = api_key
        self.secret = secret
        self.api_url = api_url if api_url else 'https://api.sailthru.com'
        self.last_rate_limit_info = {}

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
        data = {'template': template,
                'email': email,
                'vars': _vars,
                'options': options.copy()}
        if limit:
            data['limit'] = limit.copy()
        if schedule_time is not None:
            data['schedule_time'] = schedule_time
        return self.api_post('send', data)

    def multi_send(self, template, emails, _vars=None, evars=None, schedule_time=None, options=None):
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
        data = {'template': template,
                'email': ','.join(emails) if isinstance(emails, list) else emails,
                'vars': _vars.copy(),
                'evars': evars.copy(),
                'options': options.copy()}
        if schedule_time is not None:
            data['schedule_time'] = schedule_time
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
        DEPRECATED!
        get user email data
        http://docs.sailthru.com/api/email
        """
        data = {'email': email}
        return self._api_request('email', data, 'GET')

    def set_email(self, email, _vars=None, lists=None, templates=None, verified=0, optout=None, send=None, send_vars=None):
        """
        DEPRECATED!
        Update information about one of your users, including adding and removing the user from lists.
        http://docs.sailthru.com/api/email
        """
        _vars = _vars or {}
        lists = lists or []
        templates = templates or []
        send_vars = send_vars or []
        data = {'email': email,
                'vars':  _vars.copy(),
                'lists': lists,
                'templates': templates,
                'verified': int(verified)}
        if optout is not None:
            data['optout'] = optout
        if send is not None:
            data['send'] = send
        if send_vars:
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

    def schedule_blast_from_template(self, template, list_name, schedule_time, options=None):
        """
        Schedule a mass mail blast from template
        http://docs.sailthru.com/api/blast
        @param template: template to copy from
        @param list_name: list to send to
        @param schedule_time
        @param options: additional optional params
        """
        options = options or {}
        data = options.copy()
        data['copy_template'] = template
        data['list'] = list_name
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

    def update_blast(self, blast_id, name=None, list=None, schedule_time=None, from_name=None, from_email=None,
                     subject=None, content_html=None, content_text=None, options=None):
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
        data = {'blast_id': blast_id,
                'schedule_time': ''}
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
        data = {'template': template}
        if template_fields:
            data.update(template_fields)
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
        return self.api_get('list',  {})

    def save_list(self, list_name, emails):
        """
        Upload a list. The list import job is queued and will happen shortly after the API request.
        http://docs.sailthru.com/api/list
        @param list: list name
        @param emails: List of email values or comma separated string
        """
        data = {'list': list_name,
                'emails': ','.join(emails) if isinstance(emails, list) else emails}
        return self.api_post('list', data)

    def delete_list(self, list_name):
        """
        delete given list
        http://docs.sailthru.com/api/list
        """
        return self.api_delete('list', {'list': list_name})

    def import_contacts(self, email, password, include_name=False):
        """
        Fetch email contacts from a user's address book on one of the major email websites. Currently supports AOL, Gmail, Hotmail, and Yahoo! Mail.
        """
        data = {'email': email,
                'password': password}
        if include_name:
            data['names'] = 1
        return self.api_post('contacts', data)

    def push_content(self, title, url,
                     images=None, date=None, expire_date=None,
                     description=None, location=None, price=None,
                     tags=None,
                     author=None, site_name=None,
                     spider=None, vars=None):

        """
        Push a new piece of content to Sailthru.

        Expected names for the `images` argument's map are "full" and "thumb"
        Expected format for `location` should be [longitude,latitude]

        @param title: title string for the content
        @param url: URL string for the content
        @param images: map of image names
        @param date: date string
        @param expire_date: date string for when the content expires
        @param description: description for the content
        @param location: location of the content
        @param price: price for the content
        @param tags: list or comma separated string values
        @param author: author for the content
        @param site_name: site name for the content
        @param spider: truthy value to force respidering content
        @param vars: replaceable vars dictionary

        """
        vars = vars or {}
        data = {'title': title,
                'url': url}
        if images is not None:
            data['images'] = images
        if date is not None:
            data['date'] = date
        if expire_date is not None:
            data['expire_date'] = date
        if location is not None:
            data['location'] = date
        if price is not None:
            data['price'] = price
        if description is not None:
            data['description'] = description
        if site_name is not None:
            data['site_name'] = images
        if author is not None:
            data['author'] = author
        if spider:
            data['spider'] = 1
        if tags is not None:
            data['tags'] = ",".join(tags) if isinstance(tags, list) else tags
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
        if type in ['weekly', 'daily']:
            data['when'] = when
        return self.api_post('alert', data)

    def delete_alert(self, email, alert_id):
        """
        delete user alert
        """
        data = {'email': email,
                'alert_id': alert_id}
        return self.api_delete('alert', data)

    def purchase(self, email, items=None, incomplete=None, message_id=None, options=None, extid=None):
        """
        Record that a user has made a purchase, or has added items to their purchase total.
        http://docs.sailthru.com/api/purchase
        @param email: Email string
        @param items: list of item dictionary with keys: id, title, price, qty, and url
        @param message_id: message_id string
        @param extid: external ID to track purchases
        @param options: other options that can be set as per the API documentation
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
        if extid is not None:
            data['extid'] = extid
        return self.api_post('purchase', data)

    def get_purchase(self, purchase_id, purchase_key='sid'):
        """
        Retrieve information about a purchase using the system's unique ID or a client's ID
        @param id_: a string that represents a unique_id or an extid.
        @param key: a string that is either 'sid' or 'extid'.
        """
        data = {'purchase_id': purchase_id,
                'purchase_key': purchase_key}
        return self.api_get('purchase', data)

    def stats_list(self, list=None, date=None, headers=None):
        """
        Retrieve information about your subscriber counts on a particular list, on a particular day.
        http://docs.sailthru.com/api/stat
        """
        data = {'stat': 'list'}
        if list is not None:
            data['list'] = list
        if date is not None:
            data['date'] = date
        return self._stats(data, headers)

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

    def stats_send(self, template, start_date, end_date, options=None):
        """
        Retrieve information about a particular transactional or aggregated information
        from transactionals from that template over a specified date range.
        http://docs.sailthru.com/api/stat
        """
        options = options or {}
        data = options.copy()
        data = {'template': template,
                'start_date': start_date,
                'end_date': end_date
                }
        data['stat'] = 'send'
        return self._stats(data)

    def _stats(self, data, headers=None):
        """
        Make Stats API Request
        """
        return self.api_get('stats', data, headers)

    def receive_verify_post(self, post_params):
        """
        Returns true if the incoming request is an authenticated verify post.
        """
        if isinstance(post_params,  dict):
            required_params = ['action', 'email', 'send_id', 'sig']
            if not self.check_for_valid_postback_actions(required_params, post_params):
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
            if 'email' not in send_body:
                return False
            if send_json['email'] != post_params['email']:
                return False
        except ValueError:
            return False

        return True

    def receive_update_post(self, post_params):
        """
        Update postbacks
        """

        if isinstance(post_params, dict):
            required_params = ['action', 'email', 'sig']
            if not self.check_for_valid_postback_actions(required_params, post_params):
                return False
        else:
            return False

        if post_params['action'] != 'update':
            return False

        signature = post_params['sig']
        post_params = post_params.copy()
        del post_params['sig']

        if signature != get_signature_hash(post_params, self.secret):
            return False

        return True

    def receive_optout_post(self, post_params):
        """
        Optout postbacks
        """
        if isinstance(post_params,  dict):
            required_params = ['action', 'email', 'sig']
            if not self.check_for_valid_postback_actions(required_params, post_params):
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
        if isinstance(post_params, dict):
            required_params = ['action', 'email', 'sig']
            if not self.check_for_valid_postback_actions(required_params, post_params):
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
            if not send_response.is_ok():
                return False
            send_obj = send_response.get_body()
            if not send_obj or 'email' not in send_obj:
                return False

        # for blasts
        if 'blast_id' in post_params:
            blast_id = post_params['blast_id']
            blast_response = self.get_blast(blast_id)
            if not blast_response.is_ok():
                return False
            blast_obj = blast_response.get_body()
            if not blast_obj:
                return False

        return True

    def check_for_valid_postback_actions(self, required_keys, post_params):
        """
        checks if post_params contain required keys
        """
        for key in required_keys:
            if key not in post_params:
                return False
        return True

    def api_get(self, action, data, headers=None):
        """
        Perform an HTTP GET request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'GET', headers)

    def api_post(self, action, data, binary_data_param=None):
        """
        Perform an HTTP POST request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        binary_data_param = binary_data_param or []
        if binary_data_param:
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
        data = data.copy()

        try:
            file_handles = []
            for param in binary_data_param:
                if param in data:
                    binary_data[param] = file_handle = open(data[param], 'r')
                    file_handles.append(file_handle)
                    del data[param]
            json_payload = self._prepare_json_payload(data)

            return self._http_request(action, json_payload, "POST", binary_data)
        finally:
            for file_handle in file_handles:
                file_handle.close()

    def api_delete(self, action, data):
        """
        Perform an HTTP DELETE request, using the shared-secret auth hash.
        @param action: API action call
        @param data: dictionary values
        """
        return self._api_request(action, data, 'DELETE')

    def _api_request(self, action, data, request_type, headers=None):
        """
        Make Request to Sailthru API with given data and api key, format and signature hash
        """
        if 'file' in data:
            file_data = {'file': open(data['file'], 'rb')}
        else:
            file_data = None

        return self._http_request(action, self._prepare_json_payload(data), request_type, file_data, headers)

    def _http_request(self, action, data, method, file_data=None, headers=None):
        url = self.api_url + '/' + action
        file_data = file_data or {}
        response = sailthru_http_request(url, data, method, file_data, headers)
        if (action in self.last_rate_limit_info):
            self.last_rate_limit_info[action][method] = response.get_rate_limit_headers()
        else:
            self.last_rate_limit_info[action] = { method : response.get_rate_limit_headers() }
        return response

    def _prepare_json_payload(self, data):
        payload = {'api_key': self.api_key,
                   'format': 'json',
                   'json': json.dumps(data)}
        signature = get_signature_hash(payload, self.secret)
        payload['sig'] = signature
        return payload

    def get_last_rate_limit_info(self, action, method):
        """
        Get rate limit information for last API call
        :param action: API endpoint
        :param method: Http method, GET, POST or DELETE
        :return: dict|None
        """
        method = method.upper()
        if (action in self.last_rate_limit_info and method in self.last_rate_limit_info[action]):
            return self.last_rate_limit_info[action][method]

        return None