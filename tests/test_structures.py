import unittest
import mcore as mc
from common import *

class TestNeuron(unittest.TestCase):
    def test_make_layer(self):
        pkg = mc.Package.make_empty()
        builder = mc.StructsBuilder()
        layer_size = 1000

        def neuron_builder(l_index:int):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        layer_name, ids, pkg = builder.make_layer(pkg, layer_size, neuron_builder)

        self.assertTrue(bool(layer_name))
        self.assertTrue(bool(ids))
        self.assertTrue(pkg.isValid())
        self.assertFalse(pkg.empty())
        self.assertEqual(len(pkg.neurons), layer_size)
        self.assertEqual(len(ids), layer_size)
        for n in pkg.neurons:
            self.assertEqual(n["energyLeak"], 0.1)
            self.assertEqual(n["peakEnergy"], 5.)
            self.assertEqual(n["currentEnergy"], 0.)