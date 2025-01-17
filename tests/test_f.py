import unittest
import os
import mcore as mc
import unittest
import pandas as pd
from common import F

class TestF(unittest.TestCase):
    def test_d_eq(self):
        a = {"a":1,"b":2,"c":1,"d":2}
        b = {"a":1,"b":2,"c":1,"d":2}
        c = {"a":1,"b":2,"c":3,"d":2}
        d = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":1,"d":2}}
        d2 = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":1,"d":2}}
        e = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":2,"d":2}}
        self.assertTrue(F.d_eq(a, a))
        self.assertTrue(F.d_eq(d, d))
        self.assertTrue(F.d_eq(e, e))
        self.assertTrue(F.d_eq(None, None, maybe_none=True))
        self.assertFalse(F.d_eq(a, None, maybe_none=True))
        self.assertTrue(F.d_eq(None, None, maybe_none=True))
        self.assertFalse(F.d_eq(None, a, maybe_none=True))
        self.assertTrue(F.d_eq(a, b))
        self.assertTrue(F.d_eq(b, a))
        self.assertFalse(F.d_eq(a, c))
        self.assertFalse(F.d_eq(b, c))
        self.assertFalse(F.d_eq(c, a))
        self.assertFalse(F.d_eq(c, b))
        self.assertFalse(F.d_eq(c, d))
        self.assertFalse(F.d_eq(d, c))
        self.assertTrue(F.d_eq(d, d2))
        self.assertFalse(F.d_eq(d, e))
        self.assertFalse(F.d_eq(d2, e))

    # Test the length of a random ID generated by the random_id() function
    def test_random_id_length(self):
        # Check that the length of the generated ID is equal to the specified length
        length = 10
        token = F.random_id(length)
        self.assertEqual(len(token), length)

    # Test that an empty dictionary is correctly sorted by the dsort() function
    def test_dsort_empty_dict(self):
        # Create an empty dictionary
        dict = {}
        # Sort the dictionary and check that its length is zero
        sorted_dict = F.dsort(dict)
        self.assertEqual(len(sorted_dict), 0)

    # Test that two lists are considered equal by the l_eq() function
    def test_l_eq_equal_list(self):
        # Create two lists with the same elements
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        # Check that the lists are equal
        self.assertTrue(F.l_eq(list1, list2))

    # Test that two empty dictionaries are considered equal by the d_eq() function
    def test_d_eq_empty_dicts(self):
        # Create two empty dictionaries
        dict1 = {}
        dict2 = {}
        # Check that the dictionaries are equal
        self.assertTrue(F.d_eq(dict1, dict2))

    # Test that two non-empty dictionaries are not considered equal by the d_eq() function
    def test_d_eq_dict_values(self):
        # Create two non-empty dictionaries with different values
        dict1 = {"a": 1, "b": 2}
        dict2 = {"a": 3, "b": 4}
        # Check that the dictionaries are not equal
        self.assertFalse(F.d_eq(dict1, dict2))

    # Test that an empty dictionary is correctly sorted by value using the dsort_val() function
    def test_dsort_val_empty_dict(self):
        # Create an empty dictionary
        dict = {}
        # Sort the dictionary and check that its length is zero
        sorted_dict = F.dsort_val(dict)
        self.assertEqual(len(sorted_dict), 0)

    # Test that a new token is correctly generated by the generateToken() function
    def test_generateToken(self):
        # Generate two tokens
        token1 = F.generateToken()
        token2 = F.generateToken()
        # Check that the tokens are not equal
        self.assertNotEqual(token1, token2)

    # Test that a node name is correctly generated by the getNodeName() function
    def test_getNodeName(self):
        # Generate a new node name
        name_hash = F.getNodeName()
        # Check that the result is a string
        self.assertIsInstance(name_hash, str)

    # Test that an ID is correctly generated by the generateOID() function
    def test_generateOID(self):
        # Generate two IDs
        id1 = F.generateOID()
        id2 = F.generateOID()
        # Check that the IDs are not equal
        self.assertNotEqual(id1, id2)
