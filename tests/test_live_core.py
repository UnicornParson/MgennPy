import unittest
import pandas as pd
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
        exp_i_names = ['Alias1', 'Alias2', 'Alias3', 'Alias4', 'Alias5', 'Alias6', 'Alias7', 'Alias8', 'Alias9']

        self.assertEqual(names.sort(), exp_i_names.sort())
        row = mc.TapeInputsRow(len(names), float)
        row.headers = names
        for i in range (len(names)):
            amp = 11.0 / (float(i) + 0.1)
            row.data[i] = amp
        core.update_inputs(row)
        record = core.exec()
        self.assertFalse(core.empty())
        self.assertFalse(core.is_dirty())
        self.assertNotEqual(record, None)
        self.assertTrue(isinstance(record.data, pd.DataFrame))
        exp_o_names = ["out0",  "out1",  "out2",  "out3",  "out4",  "out5",  "out6",  "out7",  "out8",  "out9"]
        F.print(f"o_record: {record.data}")
        self.assertEqual(list(record.data.columns.values).sort(), exp_o_names.sort())

    def test_pd_to_pd(self):
        pkg = mc.Package.make_empty()
        