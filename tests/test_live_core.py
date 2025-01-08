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
        n1 = pkg.new_neuron(leak=1.0, peak=5.0, receivers=[])
        i1 = pkg.new_tape_input("i1", [])
        o1 = pkg.new_output("o1")

        l1 = pkg.new_link_between(apt=0.0, length=1, src=i1, dst=n1)
        l2 = pkg.new_link_between(apt=0.0, length=1, src=n1, dst=o1)
        ce = mc.Engine()
        ce.core = mc.Core()
        ce.core.load(pkg)
        ce.tick_offset = 0
        spkg = ce.core.dump()
        sdata = spkg.dumpJsonStr()


        df_expected = pd.DataFrame([0.0]*7 + [5.0] + [0.0]*4, columns=['o1_exp'])
        df_in = pd.DataFrame([3,0] * 6, columns=['i1'])
        ticks = 12
        df_out = pd.DataFrame()
        for t in range(ticks):
            df_out = pd.concat([df_out, ce.run_once(df_in)], ignore_index=True)

        io = pd.concat([df_in, df_out, df_expected], axis=1)
        io['error'] = io['o1'].astype(float) - io['o1_exp'].astype(float)
        for index, row in io.iterrows():
            self.assertEqual(row["o1"], row["o1_exp"])
            self.assertEqual(row["error"], 0.0)
        # cleanup
        ce.core = None
        ce = None
        pkg = None
        df_out = None
        io = None
        # save - restore - retest
        rpkg = mc.Package()
        rpkg.loadJsonStr(sdata)
        self.assertTrue(rpkg.isValid())
        self.assertEqual(len(rpkg.inputs), 1)
        self.assertEqual(len(rpkg.neurons), 1)
        self.assertEqual(len(rpkg.outputs), 1)
        r_engine = mc.Engine()
        r_engine.core = mc.Core()
        r_engine.core.load(rpkg)
        r_engine.tick_offset = 0
        df_out = pd.DataFrame()
        df_expected = pd.DataFrame([0.0]*7 + [5.0] + [0.0]*4, columns=['o1_exp'])
        df_in = pd.DataFrame([3,0] * 6, columns=['i1'])
        energy = []
        print(sdata)
        for t in range(ticks):
            df_out = pd.concat([df_out, r_engine.run_once(df_in)], ignore_index=True)
            
        io = pd.concat([df_in, df_out, df_expected], axis=1)
        io['error'] = io['o1'].astype(float) - io['o1_exp'].astype(float)
        for index, row in io.iterrows():
            self.assertEqual(row["o1"], row["o1_exp"])
            self.assertEqual(row["error"], 0.0)

