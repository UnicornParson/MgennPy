import unittest
from unittest.mock import Mock, patch
import math
import inspect
import numpy as np
import mcore as mc
from common import *
from utils import TestUtils

class TestNeuron(unittest.TestCase):
    def __del__(self):
        F.set_print_token("")

    def test_make_layer(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        builder = mc.StructsBuilder()
        layer_size = 10
    
        def neuron_builder(l_index:int):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        layer_info, pkg = builder.make_layer(pkg, layer_size, neuron_builder)

        self.assertTrue(bool(layer_info.layer_name))
        self.assertTrue(bool(layer_info.ids))
        self.assertTrue(pkg.isValid())
        self.assertFalse(pkg.empty())
        self.assertEqual(len(pkg.neurons), layer_size)
        self.assertEqual(len(layer_info.ids), layer_size)
        for n in pkg.neurons:
            self.assertEqual(n["energyLeak"], 0.1)
            self.assertEqual(n["peakEnergy"], 5.)
            self.assertEqual(n["currentEnergy"], 0.)
        F.set_print_token("")

    def test_make_ngrid(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        builder = mc.StructsBuilder()
        grid_shape = (3, 3, 3)
        def neuron_builder(l_index):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        layer_info, pkg = builder.make_ngrid(pkg, grid_shape, neuron_builder)
        ids = layer_info.ids
        sh = ids.shape
        self.assertTrue(isinstance(ids, np.ndarray))
        self.assertTrue(bool(layer_info.layer_name))
        self.assertTrue(bool(sh))
        self.assertEqual(sh, grid_shape)
        sz = math.prod(grid_shape)
        self.assertEqual(len(pkg.neurons), sz)
        for n in pkg.neurons:
            self.assertEqual(n["energyLeak"], 0.1)
            self.assertEqual(n["peakEnergy"], 5.)
            self.assertEqual(n["currentEnergy"], 0.)
        F.set_print_token("")

    def test_connect_layers_1_1(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        builder = mc.StructsBuilder()
        grid_shape = (3, 3, 3)
        def neuron_builder(l_index):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        def link_builder(from_id, to_id):
            apt = 1.
            length = 1
            return (apt, length)
        sz = math.prod(grid_shape)
        l_layer_info, pkg = builder.make_ngrid(pkg, grid_shape, neuron_builder)
        r_layer_info, pkg = builder.make_ngrid(pkg, grid_shape, neuron_builder)
        l_ids = l_layer_info.ids
        r_ids = r_layer_info.ids
        self.assertTrue(bool(l_layer_info.layer_name))
        self.assertTrue(bool(r_layer_info.layer_name))
        self.assertNotEqual(l_layer_info.layer_name, r_layer_info.layer_name)
        self.assertEqual(len(pkg.neurons), sz*2)
        self.assertTrue(pkg.isValid())
        links, pkg = builder.connect_layers_1_1(pkg, l_ids, r_ids, link_builder)
        self.assertTrue(pkg.isValid())
        self.assertEqual(len(links), sz)
        self.assertEqual(len(pkg.links), sz)

        # no new neurons
        self.assertEqual(len(pkg.neurons), sz*2)
        self.assertTrue(bool(l_layer_info.layer_name))

        # not broken
        pkgName, pkg_data = pkg.dump()
        self.assertTrue(bool(pkgName))
        self.assertTrue(bool(pkg_data))
        F.set_print_token("")

    def test_connect_layers_all(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        builder = mc.StructsBuilder()
        grid_shape_l = (2, 2, 2)
        grid_shape_r = (2, 2, 2)

        if TestUtils.run_long_tests():
            grid_shape_l = (3, 4, 5)
            grid_shape_r = (6, 7, 8)
        def neuron_builder(l_index:int):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        def link_builder(from_id:int, to_id:int):
            apt = 1.
            length = 1
            return (apt, length)
        sz_l = math.prod(grid_shape_l)
        sz_r = math.prod(grid_shape_r)
        l_layer_info, pkg = builder.make_ngrid(pkg, grid_shape_l, neuron_builder)
        r_layer_info, pkg = builder.make_ngrid(pkg, grid_shape_r, neuron_builder)
        l_ids = l_layer_info.ids
        r_ids = r_layer_info.ids
        self.assertTrue(bool(l_layer_info.layer_name))
        self.assertTrue(bool(r_layer_info.layer_name))
        self.assertNotEqual(l_layer_info.layer_name, r_layer_info.layer_name)
        self.assertEqual(len(pkg.neurons), (sz_l + sz_r))
        self.assertTrue(pkg.isValid())
        links, pkg = builder.connect_layers_all(pkg, l_ids, r_ids, link_builder)
        self.assertTrue(pkg.isValid())
        self.assertEqual(len(links), sz_l*sz_r)
        self.assertEqual(len(pkg.links), sz_l*sz_r)

        # no new neurons
        self.assertEqual(len(pkg.neurons), (sz_l + sz_r))

        # not broken
        pkgName, pkg_data = pkg.dump()
        self.assertTrue(bool(pkgName))
        self.assertTrue(bool(pkg_data))
        F.set_print_token("")

    def test_neuron_builder(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        builder = mc.StructsBuilder()
        leak, peak = builder.neuron_builder(0)
        self.assertEqual(leak, 0.)
        self.assertEqual(peak, 5.)
        F.set_print_token("")

class TestLayerInfo(unittest.TestCase):
    def test_to_dict_and_from_dict_list(self):
        li = mc.LayerInfo()
        li.layer_name = "test_layer"
        li.content_type = mc.LayerInfo.CONTENT_TYPE_NEURONS
        li.ids_type = list
        li.ids = [1, 2, 3]
        li.shape = (3,)
        li.dims = 1
        d = li.to_dict()
        li2 = mc.LayerInfo().from_dict(d)
        self.assertEqual(li2.layer_name, li.layer_name)
        self.assertEqual(li2.content_type, li.content_type)
        self.assertEqual(li2.ids_type, list)
        self.assertEqual(li2.ids, [1, 2, 3])
        self.assertEqual(li2.shape, (3,))
        self.assertEqual(li2.dims, 1)

    def test_to_dict_and_from_dict_ndarray(self):
        li = mc.LayerInfo()
        li.layer_name = "test_grid"
        li.content_type = mc.LayerInfo.CONTENT_TYPE_NEURONS
        li.ids_type = np.ndarray
        li.ids = np.array([[1, 2], [3, 4]], dtype=np.int64)
        li.shape = li.ids.shape
        li.dims = 2
        d = li.to_dict()
        li2 = mc.LayerInfo().from_dict(d)
        self.assertEqual(li2.layer_name, li.layer_name)
        self.assertEqual(li2.content_type, li.content_type)
        self.assertEqual(li2.ids_type, np.ndarray)
        self.assertTrue(np.array_equal(li2.ids, li.ids))
        self.assertEqual(li2.shape, (2, 2))
        self.assertEqual(li2.dims, 2)

    def test_from_dict_missing_key(self):
        d = {
            "layer_name": "test",
            "content_type": mc.LayerInfo.CONTENT_TYPE_NEURONS,
            "dims": 1,
            "ids_type": "list"
            # 'ids' is missing
        }
        with self.assertRaises(ValueError):
            mc.LayerInfo().from_dict(d)

    def test_from_dict_invalid_ids_type(self):
        d = {
            "layer_name": "test",
            "content_type": mc.LayerInfo.CONTENT_TYPE_NEURONS,
            "dims": 1,
            "ids_type": "unknown_type",
            "ids": [1, 2, 3]
        }
        with self.assertRaises(ValueError):
            mc.LayerInfo().from_dict(d)
