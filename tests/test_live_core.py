import unittest
import mcore as mc
import os
from common import *

class TestLiveCore(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"

    def test_load_exec(self):
        pkg = mc.Package()
        pkg.loadFile(self.__pkg_path)
        core = mc.Core()
        core.load(pkg)
        self.assertFalse(core.empty())
        self.assertFalse(core.is_dirty())
        names = core.input_names()
        exp_names = ['Alias1', 'Alias2', 'Alias3', 'Alias4', 'Alias5', 'Alias6', 'Alias7', 'Alias8', 'Alias9']
        self.assertEqual(names.sort(), exp_names.sort())
        row = mc.TapeInputsRow(len(names), float)
        row.headers = names
        for i in range (len(names)):
            amp = 11.0 / (float(i) + 0.1)
            row.data[i] = amp
        core.update_inputs(row)
        core.exec()
        self.assertFalse(core.empty())
        self.assertFalse(core.is_dirty())