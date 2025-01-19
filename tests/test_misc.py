import unittest
import pandas as pd
import mcore as mc
import numpy as np
import os
from common import *

class TestObjectFactory(unittest.TestCase):
    def setUp(self):
        self.factory = ObjectFactory()

    def test_makeNeuronData_default_values(self):
        data = self.factory.makeNeuronData(0, 0, id=10)
        expected_data = {
            "currentEnergy": 0,
            "energyLeak": 0,
            "mode": "shared",
            "peakEnergy": 0,
            "receivers": [],
            "id": 10
        }
        self.assertTrue(F.d_eq(data, expected_data))

    def test_makeNeuronData_custom_values(self):
        data = self.factory.makeNeuronData(1.5, 2.1, currentEnergy=3.14, id=10)
        expected_data = {
            "currentEnergy": 3.14,
            "energyLeak": 2.1,
            "mode": "shared",
            "peakEnergy": 1.5,
            "receivers": [],
            "id": 10
        }
        self.assertTrue(F.d_eq(data, expected_data))

    def test_makeNeuronData_custom_id(self):
        data = self.factory.makeNeuronData(1.5, 2.1, id=10)
        expected_data = {
            "currentEnergy": 0,
            "energyLeak": 2.1,
            "mode": "shared",
            "peakEnergy": 1.5,
            "receivers": [],
            "id": 10
        }
        self.assertTrue(F.d_eq(data, expected_data))

    def test_makeNeuronData_custom_receivers(self):
        receivers = [1, 2, 3]
        data = self.factory.makeNeuronData(1.5, 2.1, receivers=receivers, id=10)
        expected_data = {
            "currentEnergy": 0,
            "energyLeak": 2.1,
            "mode": "shared",
            "peakEnergy": 1.5,
            "receivers": [1, 2, 3],
            "id": 10
        }
        self.assertTrue(F.d_eq(data, expected_data))

    def test_makeNeuronData_custom_all_params(self):
        data = self.factory.makeNeuronData(1.5, 2.1, currentEnergy=3.14, id=10, receivers=[1, 2, 3])
        expected_data = {
            "currentEnergy": 3.14,
            "energyLeak": 2.1,
            "mode": "shared",
            "peakEnergy": 1.5,
            "receivers": [1, 2, 3],
            "id": 10
        }
        self.assertTrue(F.d_eq(data, expected_data))
