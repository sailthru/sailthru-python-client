# -*- coding: utf-8 -*-
"""
Tests for sailthru_client
"""
from mock import MagicMock
import unittest
import sys

#sys.path.append('../')

sys.path[0:0] = [""]

import sailthru.sailthru_http
from sailthru import sailthru_client as c


class TestSailthruClientFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_params_with_simple_dictionary(self):
        _dict = {'unix': ['Linux', 'Mac', 'Solaris'], 'windows': 'None'}
        expected = sorted(['Linux', 'Mac', 'Solaris', 'None'])
        extracted = sorted(c.extract_params(_dict))
        self.assertEqual(extracted, expected)

    def test_extract_params_with_embedded_dictionary(self):

        _dict = {'US': [{'New York': ['Queens', 'New York', 'Brooklyn']}, 'Virginia', 'Washington DC', 'Maryland'], 'Canada': ['Ontario', 'Quebec', 'British Columbia']}
        expected = sorted(['Queens', 'New York', 'Brooklyn', 'Virginia', 'Washington DC', 'Maryland', 'Ontario', 'Quebec', 'British Columbia'])
        extracted = sorted(c.extract_params(_dict))
        self.assertEqual(extracted, expected)

    def test_signature_string(self):
        secret = '123456'
        _dict = {'unix': ['Linux', 'Mac', 'Solaris'], 'windows': 'None'}
        expected_list = ['Linux', 'Mac', 'Solaris', 'None']
        expected_list.sort()
        expected = secret + "".join(expected_list)
        self.assertEqual(c.get_signature_string(_dict, secret), expected)

class TestSailthruClient(unittest.TestCase):
    def setUp(self):
        api_key = 'test'
        api_secret = 'super_secret'
        self.client = c.SailthruClient(api_key, api_secret)

    def test_check_for_valid_actions(self):
        required_keys = ['email', 'action', 'sig']
        invalid_params_dict = {'email': 'praj@sailthru.com', 'action': 'optout', 'sig__': '125342352'}
        self.assertFalse(self.client.check_for_valid_postback_actions(required_keys, invalid_params_dict))

        empty_dict = {}
        self.assertFalse(self.client.check_for_valid_postback_actions(required_keys, empty_dict))

        empty_list = []
        self.assertFalse(self.client.check_for_valid_postback_actions(required_keys, empty_list))

        valid_params_dict = {'email': 'praj@sailthru.com', 'action': 'optout', 'sig': '125342352'}
        self.assertTrue(self.client.check_for_valid_postback_actions(required_keys, valid_params_dict))

    def test_receive_verify_post(self):
        mock_http_request = MagicMock()
        mock_http_request.return_value.get_body.return_value = '{"email":"menglander@sailthru.com"}'

        self.client._http_request = mock_http_request

        mock_get_signature_hash = MagicMock()
        mock_get_signature_hash.return_value = 'sighelloworld'
        sailthru.sailthru_client.get_signature_hash = mock_get_signature_hash

        post_params = {}
        post_params['action'] = 'verify'
        post_params['email'] = 'menglander@sailthru.com'
        post_params['send_id'] = 'abc123'
        post_params['sig'] = 'sighelloworld'

        actual = self.client.receive_verify_post(post_params)
        expected = True
        self.assertEqual(actual, expected)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSailthruClientFunctions('test_default_size'))
    return suite

if __name__ == '__main__':
    unittest.main()
