import unittest
import mcore as mc
import os
from common import *

class TestCore(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
        self.__powered_pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev1_powered.pkg"
        
    def test_check_examplee(self):
        self.assertTrue(os.path.isfile(self.__pkg_path))

    def test_empty_core(self):
        core = mc.Core()
        self.assertTrue(core.empty())
        pkg = core.dump()
        e = core.total_energy()
        self.assertEqual(e, 0.0)
        e = pkg.total_energy()
        self.assertEqual(e, 0.0)
        self.assertTrue(pkg.isValid())
        self.assertTrue(pkg.empty())

    def test_measure_powered_core(self):
        pkg = mc.Package()
        pkg.loadFile(self.__powered_pkg_path)
        self.assertEqual(pkg.total_energy(), 10.0)
        core = mc.Core()
        core.load(pkg)
        self.assertFalse(core.empty())
        self.assertEqual(core.total_energy(), 10.0)

        cloned_pkg = pkg.clone()
        self.assertEqual(cloned_pkg.total_energy(), 10.0)
        cloned_pkg.removeDynamic()
        self.assertEqual(cloned_pkg.total_energy(), 0.0)
        core.removeDynamic()
        self.assertEqual(core.total_energy(), 0.0)


    def test_load_from_file(self):
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        core = mc.Core()
        core.load(pkg)
        self.assertFalse(core.empty())

        neurons = core.neurons()
        self.assertEqual(len(neurons), 10)
        for n in neurons:
            self.assertNotEqual(n, None)
            self.assertNotEqual(n.id(), MgennConsts.NULL_ID)

        links = core.links()
        self.assertEqual(len(links), 10)
        for l in links:
            self.assertNotEqual(l, None)
            self.assertNotEqual(l.id(), MgennConsts.NULL_ID)

        outputs = core.links()
        self.assertEqual(len(outputs), 10)
        for o in outputs:
            self.assertNotEqual(o, None)
            self.assertNotEqual(o.id(), MgennConsts.NULL_ID)
        max_id = core.max_id()
        next_id = core.next_id()
        self.assertEqual(max_id, 109)
        self.assertEqual(max_id, core.max_id()) ## second call. not inremented
        self.assertEqual(next_id, 110)
        self.assertEqual(core.next_id(), next_id) ## second call. not inremented

        self.assertNotEqual(next_id, max_id)
        self.assertTrue(core.__contains__(max_id))
        self.assertFalse(core.__contains__(next_id))

    def test_dump_core(self):
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)

        self.assertTrue(pkg.isValid())
        orig = pkg.clone()
        self.assertTrue(orig.isValid())
        self.assertEqual(orig.meta["name"], "4d014c646eab1cd96f7e1bf5ab8f1a905f9a68b6fee7faa4c0cd5345496cc95ef619856e2f44c32ecb0135af7a419b78787da787b48713b40e35c0e517132073:13388.1504363103804.18")
        core = mc.Core()
        core.load(pkg)

        new_pkg = core.dump()
        self.assertTrue(new_pkg.isValid())
        self.assertTrue(bool(new_pkg.inputs))
        self.assertTrue(bool(new_pkg.outputs))
        self.assertTrue(bool(new_pkg.links))
        self.assertTrue(bool(new_pkg.neurons))
        pkgName, pkg_data = new_pkg.dump()

        self.assertTrue(bool(pkgName))
        self.assertTrue(bool(pkg_data))
        self.assertTrue("content" in pkg_data)
        pkg_content = pkg_data["content"]

        self.assertTrue("inputs" in pkg_content)
        self.assertTrue("outputs" in pkg_content)
        self.assertTrue("storage" in pkg_content)

        self.assertTrue("links" in pkg_content["storage"])
        self.assertTrue("neurons" in pkg_content["storage"])

        self.assertEqual(len(pkg_content["inputs"]), len(orig.inputs))
        self.assertEqual(len(pkg_content["outputs"]), len(orig.outputs))
        self.assertEqual(len(pkg_content["storage"]["links"]), len(orig.links))
        self.assertEqual(len(pkg_content["storage"]["neurons"]), len(orig.neurons))

        self.assertTrue(PackageUtils.checkRawPkg_b(pkg_data))

        self.assertTrue(new_pkg.meta)
        self.assertEqual(new_pkg.meta["branch"], "testns")
        self.assertEqual(new_pkg.meta["branchSeq"], 1)
        self.assertEqual(new_pkg.meta["generation"], 0)
        self.assertNotEqual(new_pkg.meta["name"], orig.meta["name"])
        self.assertEqual(new_pkg.meta["parentSnapshot"], orig.meta["name"])
        self.assertEqual(new_pkg.meta["rev"], orig.meta["rev"])
        self.assertEqual(new_pkg.meta["tick"], orig.meta["tick"]) ## not executed yet

        # all objects restored
        self.assertEqual(len(new_pkg.inputs), len(orig.inputs))
        self.assertEqual(len(new_pkg.outputs), len(orig.outputs))
        self.assertEqual(len(new_pkg.links), len(orig.links))
        self.assertEqual(len(new_pkg.neurons), len(orig.neurons))


