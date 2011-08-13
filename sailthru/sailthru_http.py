import urllib2, urllib

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

def sailthru_http_request(url, data, method):
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
        req.add_header('User-Agent', 'Sailthru API Python Client')
        req.get_method = lambda: method
        response = opener.open(req)
        response_data = response.read()
        response.close()
        return response_data
    except urllib2.HTTPError, e:
        return e.read()
    except urllib2.URLError, e:
        return str(e)