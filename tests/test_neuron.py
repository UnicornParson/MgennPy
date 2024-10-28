import unittest
import mcore as mc
from common import *

class TestNeuron(unittest.TestCase):
	def test_valid_id(self):
		neuron = mc.Neuron()
		self.assertEqual(neuron.id(), MgennConsts.NULL_ID)

	def test_keys(self):
		neuron = mc.Neuron()
		k = neuron.required_keys()
		self.assertIsInstance(k, list)
		self.assertEqual(len(k), 5)
	
	def __make_neuron(self):
		neuron = mc.Neuron()
		neuron.localId = 33
		neuron.currentEnergy = 1.0
		neuron.energyLeak = 2.0
		neuron.peakEnergy = 3.0
		neuron.mode = "eeee"
		neuron.receivers = [53]

	def test_add_mixed_numbers(self):
		data  = {
			"currentEnergy": 99.9,
			"energyLeak": 88.8,
			"mode": "mmm",
			"peakEnergy": 77.7,
			"receivers": [6, 5]
		}
		neuron = mc.Neuron()
		neuron.deserialize(data)
		self.assertEqual(neuron.currentEnergy, 99.9)
		self.assertEqual(neuron.energyLeak, 88.8)
		self.assertEqual(neuron.mode, "mmm")
		self.assertEqual(neuron.peakEnergy, 77.7)
		self.assertEqual(neuron.receivers.sort(), [6, 5].sort())


if __name__ == '__main__':
	unittest.main()