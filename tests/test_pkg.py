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
        self.assertTrue(F.l_eq(pkg.inputs, rpkg.inputs))
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

