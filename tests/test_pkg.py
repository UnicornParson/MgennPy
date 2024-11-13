import unittest
import mcore as mc
import os
from common import *

class TestPkg(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    def test_load_example(self):
        
        print(f"TestPkg {self.__pkg_path}")
        self.assertTrue(os.path.isfile(self.__pkg_path))