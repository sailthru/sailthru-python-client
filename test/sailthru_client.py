# -*- coding: utf-8 -*-
"""
Tests for sailthru_client
"""
import unittest
import sys

sys.path.append('../')

from sailthru import *

class TestSailthruClientFunctions(unittest.TestCase):
    def setup(self):
        pass

    def test_verify_purchase_items_empty(self):
        items = {}
        self.assertFalse(verify_purchase_items(items))

    def test_verify_purchase_items_non_dictionary(self):
        items = []
        self.assertFalse(verify_purchase_items(items))
        items = 'aaa'
        self.assertFalse(verify_purchase_items(items))

    def test_verify_purchase_items_valid(self):
        item = {}
        item['id'] = 2626
        item['title'] = 'unix is awesome'
        item['price'] = 236363
        item['qty'] = 25
        item['url'] = 'http://example.com/unix-is-awesome'
        items = []
        items.append(item)
        self.assertTrue(verify_purchase_items(items))

        item2 = {}
        item2['id'] = 2
        item2['title'] = 'linux is awesome'
        item2['price'] = 2363
        item2['qty'] = 2
        item2['url'] = 'http://example.com/linux-is-awesome'
        items.append(item)
        self.assertTrue(verify_purchase_items(items))

if __name__ == '__main__':
    unittest.main()