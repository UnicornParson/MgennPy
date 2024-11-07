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
		return neuron

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

	def test_leak(self):
		n = mc.Neuron()
		n.energyLeak = .1
		n.peakEnergy = 2.
		test_data = ([0.] * 18) +  [2.] + ([0.] * 18) +  [2.]
		for i, expected in enumerate(test_data):
			n.onSignal(i, .2)
			tick_rc = n.onTick(i)
			self.assertEqual(tick_rc, expected)
			print(f"iter({i}) {n} ticks with {tick_rc} result ")
		self.assertEqual(n.currentEnergy, 0.)

	def test_eq(self):
		n1 = self.__make_neuron()
		n2 = self.__make_neuron()
		self.assertEqual(n1, n1)
		self.assertEqual(n2, n2)
		self.assertEqual(n1, n2)
		n1.energyLeak = .1
		self.assertEqual(n1, n1)
		self.assertNotEqual(n1, n2)

	def test_reset(self):
		n = self.__make_neuron()
		self.assertNotEqual(n.localId, MgennConsts.NULL_ID)
		self.assertNotEqual(n.currentEnergy, 0.0)
		self.assertNotEqual(n.energyLeak, 0.0)
		self.assertNotEqual(n.peakEnergy, 0.0)
		self.assertNotEqual(n.mode, "")
		self.assertNotEqual(n.receivers, 0)
		n.reset()
		self.assertEqual(n.localId, MgennConsts.NULL_ID)
		self.assertEqual(n.currentEnergy, 0.0)
		self.assertEqual(n.energyLeak, 0.0)
		self.assertEqual(n.peakEnergy, 0.0)
		self.assertEqual(n.mode, "")
		self.assertEqual(n.receivers, 0)


if __name__ == '__main__':
	unittest.main()