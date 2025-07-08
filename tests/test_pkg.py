import unittest
import mcore as mc
import os
import inspect
from common import *
from utils import TestUtils

class TestPkg(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    def __del__(self):
        F.set_print_token("")
    def test_check_examplee(self):
        self.assertTrue(os.path.isfile(self.__pkg_path))

    def test_load_from_file(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        self.assertFalse(pkg.empty())
        self.assertTrue(pkg.isValid(explain=True))
        self.assertEqual(pkg.total_energy(), 0.0)
        F.set_print_token("")

    def test_make_empty(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        self.assertTrue(pkg.empty())
        self.assertTrue(pkg.isValid(explain=True))
        self.assertEqual(pkg.total_energy(), 0.0)
        F.set_print_token("")

    def test_eq(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        pkg2 = mc.Package()
        pkg2.loadFile(self.__pkg_path)
        self.assertEqual(pkg, pkg)
        pkg2.new_neuron(0.1, 0.1, [])
        self.assertEqual(pkg2, pkg2)
        self.assertNotEqual(pkg, pkg2)
        F.set_print_token("")

    def test_pkgz(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        zdata = Pkgz.pack(pkg)
        self.assertTrue(bool(zdata))
        rpkg = Pkgz.unpack(zdata)
        self.assertFalse(rpkg.empty())
        self.assertTrue(rpkg.isValid(explain=True))
        self.assertTrue(F.d_eq(pkg.inputs, rpkg.inputs))
        self.assertTrue(F.l_eq(pkg.outputs, rpkg.outputs))
        self.assertTrue(F.l_eq(pkg.links, rpkg.links))
        self.assertTrue(F.l_eq(pkg.neurons, rpkg.neurons))
        self.assertTrue(F.d_eq(pkg.meta, rpkg.meta))
        self.assertEqual(pkg.tick, rpkg.tick)
        self.assertEqual(pkg.generation, rpkg.generation)
        self.assertEqual(pkg.seq, rpkg.seq)
        self.assertEqual(pkg.snapshot_id, rpkg.snapshot_id)
        # dont compare parent. it changed by clone
        # self.assertEqual(pkg.parent, rpkg.parent)
        self.assertEqual(pkg.state, rpkg.state)
        self.assertEqual(rpkg, pkg)
        F.set_print_token("")

    def test_serialization_and_deserialization(self):
        # Create a non-empty package
        pkg = Package.make_empty()
        in_name = 'in1'
        n1 = pkg.new_neuron(0.0, 1.0, [])
        n2 = pkg.new_neuron(0.0, 2.0, [n1])
        out_id = pkg.new_output('out1')
        pkg.new_input(in_name, 'tape', [n1, n2], {'meta': 'test'})
        pkg.links.append({'id': n1, 'receiverId': n2, 'length': 1})
        pkg.links.append({'id': n2, 'receiverId': out_id, 'length': 2})
        pkg.tick = 5
        pkg.generation = 2
        pkg.meta['custom'] = 'meta'

        # Serialize to JSON string and restore
        json_str = pkg.dumpJsonStr()
        pkg_restored = Package()
        pkg_restored.loadJsonStr(json_str)
        self.assertTrue(pkg_restored.isValid())
        # Serialize to dict and restore
        _, data = pkg.dump()
        pkg_restored2 = Package()
        pkg_restored2.loadData(data)
        self.assertTrue(pkg_restored2.isValid())

        # Сравниваем только основные содержательные поля, игнорируя snapshot_id, seq, meta['name']
        def meta_eq(m1, m2):
            m1c = dict(m1)
            m2c = dict(m2)
            m1c.pop('name', None)
            m2c.pop('name', None)
            return F.d_eq(m1c, m2c)

        for pkg_r in [pkg_restored, pkg_restored2]:
            if not F.d_eq(pkg.inputs, pkg_r.inputs):
                import pprint
                print("DIFF: pkg.inputs vs pkg_r.inputs")
                pprint.pprint(pkg.inputs)
                pprint.pprint(pkg_r.inputs)
                raise ValueError("inputs are not equal")
            self.assertTrue(F.d_eq(pkg.inputs, pkg_r.inputs))
            self.assertTrue(F.l_eq(pkg.outputs, pkg_r.outputs))
            self.assertTrue(F.l_eq(pkg.links, pkg_r.links))
            self.assertTrue(F.l_eq(pkg.neurons, pkg_r.neurons))
            self.assertEqual(pkg.tick, pkg_r.tick)
            self.assertEqual(pkg.generation, pkg_r.generation)
            self.assertEqual(pkg.state, pkg_r.state)



class TestPackageUtils(unittest.TestCase):
    def test_preset_type_check(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        with self.assertRaises(ValueError):
            PackageUtils.makeRandomContent(None, PkgSizePreset.Small)
        with self.assertRaises(ValueError):
            PackageUtils.makeRandomContent({}, PkgSizePreset.Small)
        F.set_print_token("")

    def test_preset_size(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = Package.make_empty()
        self.assertEqual(len(PackageUtils.makeRandomContent(pkg, PkgSizePreset.Small).neurons), 10)
        if TestUtils.run_long_tests():
            pkg = Package.make_empty()
            self.assertEqual(len(PackageUtils.makeRandomContent(pkg, PkgSizePreset.Medium).neurons), 100)
            pkg = Package.make_empty()
            self.assertEqual(len(PackageUtils.makeRandomContent(pkg, PkgSizePreset.Large).neurons), 1000)
        F.set_print_token("")

    def test_link_count(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = Package.make_empty()
        self.assertEqual(len(PackageUtils.makeRandomContent(pkg, PkgSizePreset.Small).links), 100) # 10x10
        self.assertEqual(len(PackageUtils.makeRandomContent(pkg, PkgSizePreset.Small).links), 200) # aone more 10x10 grid
        F.set_print_token("")

    def test_shortest_and_optimal_signal_path_length(self):
        # Create a simple package: input -> neuron -> output
        pkg = Package.make_empty()
        input_name = 'in1'
        neuron_id = pkg.new_neuron(0.0, 1.0, [])
        output_id = pkg.new_output('out1')
        # Add input
        pkg.new_input(input_name, 'tape', [neuron_id], {})
        # Link input to neuron (simulate as direct connection for graph)
        pkg.links.append({'id': input_name, 'receiverId': neuron_id, 'length': 1})
        # Link neuron to output
        pkg.links.append({'id': neuron_id, 'receiverId': output_id, 'length': 2})
        # Check shortest path (input->neuron->output): 1+2=3
        self.assertEqual(PackageUtils.shortest_signal_path_length(pkg), 3)
        # Check optimal path (must go through neuron): 3
        self.assertEqual(PackageUtils.optimal_signal_path_length(pkg), 3)

        # Add direct input->output link (length 1)
        pkg.links.append({'id': input_name, 'receiverId': output_id, 'length': 1})
        # Now shortest path: input->output (1)
        self.assertEqual(PackageUtils.shortest_signal_path_length(pkg), 1)
        # Optimal path (must go through neuron): still 3
        self.assertEqual(PackageUtils.optimal_signal_path_length(pkg), 3)

    def test_cyclic_network_paths(self):
        # Create a package with a cycle: input -> neuron1 -> neuron2 -> output, and neuron2 -> neuron1 (cycle)
        pkg = Package.make_empty()
        input_name = 'in1'
        n1 = pkg.new_neuron(0.0, 1.0, [])
        n2 = pkg.new_neuron(0.0, 1.0, [])
        out = pkg.new_output('out1')
        pkg.new_input(input_name, 'tape', [n1], {})
        # input -> n1
        pkg.links.append({'id': input_name, 'receiverId': n1, 'length': 1})
        # n1 -> n2
        pkg.links.append({'id': n1, 'receiverId': n2, 'length': 2})
        # n2 -> out
        pkg.links.append({'id': n2, 'receiverId': out, 'length': 3})
        # n2 -> n1 (cycle)
        pkg.links.append({'id': n2, 'receiverId': n1, 'length': 1})
        # Shortest path: input->n1->n2->out: 1+2+3=6
        self.assertEqual(PackageUtils.shortest_signal_path_length(pkg), 6)
        # Optimal path (must go through neuron): also 6
        self.assertEqual(PackageUtils.optimal_signal_path_length(pkg), 6)

        # Add direct input->out link (length 2)
        pkg.links.append({'id': input_name, 'receiverId': out, 'length': 2})
        # Now shortest path: input->out: 2
        self.assertEqual(PackageUtils.shortest_signal_path_length(pkg), 2)
        # Optimal path (must go through neuron): still 6
        self.assertEqual(PackageUtils.optimal_signal_path_length(pkg), 6)

        # Add another cycle: n1 -> input
        pkg.links.append({'id': n1, 'receiverId': input_name, 'length': 1})
        # Shortest and optimal paths should not change
        self.assertEqual(PackageUtils.shortest_signal_path_length(pkg), 2)
        self.assertEqual(PackageUtils.optimal_signal_path_length(pkg), 6)

    def test_invalid_package(self):
        # None as package
        with self.assertRaises(ValueError):
            PackageUtils.shortest_signal_path_length(None)
        with self.assertRaises(ValueError):
            PackageUtils.optimal_signal_path_length(None)
        # Invalid object
        class Dummy: pass
        with self.assertRaises(ValueError):
            PackageUtils.shortest_signal_path_length(Dummy())
        with self.assertRaises(ValueError):
            PackageUtils.optimal_signal_path_length(Dummy())

