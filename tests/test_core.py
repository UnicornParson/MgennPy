import unittest
import mcore as mc
import os
from common import *

class TestCore(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
        
    def test_check_examplee(self):
        self.assertTrue(os.path.isfile(self.__pkg_path))

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

