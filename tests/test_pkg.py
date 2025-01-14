import unittest
import mcore as mc
import os
from common import *

class TestPkg(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"

    def test_check_examplee(self):
        self.assertTrue(os.path.isfile(self.__pkg_path))

    def test_load_from_file(self):
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        self.assertFalse(pkg.empty())
        self.assertTrue(pkg.isValid(explain=True))
        self.assertEqual(pkg.total_energy(), 0.0)

    def test_make_empty(self):
        pkg = mc.Package.make_empty()
        self.assertTrue(pkg.empty())
        self.assertTrue(pkg.isValid(explain=True))
        self.assertEqual(pkg.total_energy(), 0.0)

    def test_eq(self):
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        pkg2 = mc.Package()
        pkg2.loadFile(self.__pkg_path)
        self.assertEqual(pkg, pkg)
        pkg2.new_neuron(0.1, 0.1, [])
        self.assertEqual(pkg2, pkg2)
        self.assertNotEqual(pkg, pkg2)

    def test_pkgz(self):
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

