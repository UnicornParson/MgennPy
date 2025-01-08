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
        F.print("load pkg ok")

    def test_make_empty(self):
        pkg = mc.Package.make_empty()
        self.assertTrue(pkg.empty())
        self.assertTrue(pkg.isValid(explain=True))
        self.assertEqual(pkg.total_energy(), 0.0)