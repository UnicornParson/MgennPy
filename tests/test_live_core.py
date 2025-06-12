import unittest
import pandas as pd
import inspect
import mcore as mc
import os
from common import *
import tqdm
class TestLiveCore(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    def __del__(self):
        F.set_print_token("")

    def _run_and_assert(self, df_input, output_name, expected, cut_expected = False):
        df_out = pd.DataFrame()
        iterations = len(df_input) - 1
        for _ in tqdm.tqdm(range(iterations)):
            df_out = pd.concat([df_out, self.engine.run_once(df_input)], ignore_index=True)
        actual = df_out[output_name].round(1).tolist()

        if cut_expected:
            expected = expected[:len(actual)]

        self.assertEqual(actual, expected, f"\nExpected: {expected}\nActual:   {actual}")

    def setUp(self):
        self.engine = mc.Engine()
        self.engine.core = mc.Core()
        self.pkg = mc.Package.make_empty()
        self.engine.tick_offset = 0

    def _takeCoreCheckpoint(self):
        if not self.engine or not self.engine.core:
            raise ValueError("no core!")
        return self.engine.core.dump()
    
    def _applyCoreCheckpoint(self, pkg):
        if not self.engine or not self.engine.core:
            raise ValueError("no core!")
        self.engine.core.load(pkg)
        self.assertFalse(self.engine.core.empty())
        self.assertFalse(self.engine.core.is_dirty())

    def test_load_exec(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
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
        F.set_print_token("")

    def test_pd_to_pd(self):
        F.set_print_token(inspect.currentframe().f_code.co_name)
        pkg = mc.Package.make_empty()
        n1 = pkg.new_neuron(leak=1.0, peak=5.0, receivers=[])
        i1 = pkg.new_tape_input("i1", [])
        o1 = pkg.new_output("o1")

        l1 = pkg.new_link_between(apt=0.0, length=1, src=i1, dst=n1)
        l2 = pkg.new_link_between(apt=0.0, length=1, src=n1, dst=o1)
        n = pkg.neurons[pkg.findNeuron(n1)]
        self.assertTrue("receivers" in n)
        self.assertNotEqual(n["receivers"], [])
        self.assertNotEqual(n["receivers"][0], o1) ## check if the output is connected to a neuron with different name than expected (it should be disconnected now). 
        
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

        for _, row in io.iterrows():
            self.assertEqual(row["o1"], row["o1_exp"], msg = f"io:\n{io.to_string(index=True)}\n")
            self.assertEqual(row["error"], 0.0, msg = f"io:\n{io.to_string(index=True)}\n")
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
        for t in range(ticks):
            df_out = pd.concat([df_out, r_engine.run_once(df_in)], ignore_index=True)
            
        io = pd.concat([df_in, df_out, df_expected], axis=1)
        io['error'] = io['o1'].astype(float) - io['o1_exp'].astype(float)
        for _, row in io.iterrows():
            self.assertEqual(row["o1"], row["o1_exp"])
            self.assertEqual(row["error"], 0.0)
        F.set_print_token("")

    def test_sequential_chain(self):
        # Network: Input -> N1 (L=2) -> N2 (L=3) -> Output
        i1 = self.pkg.new_tape_input("i1", [])
        n1 = self.pkg.new_neuron(leak=0.5, peak=4.0, receivers=[])
        n2 = self.pkg.new_neuron(leak=0.5, peak=4.0, receivers=[])
        o1 = self.pkg.new_output("o1")
        
        self.pkg.new_link_between(0.0, 2, i1, n1)
        self.pkg.new_link_between(0.0, 3, n1, n2)
        self.pkg.new_link_between(0.0, 1, n2, o1)
        
        # Input pattern: [5, 0, 5, 0...] (12 ticks)
        df_in = pd.DataFrame([5, 0] * 6, columns=['i1'])
        # Expected output accounting for link delays:
        # Total delay: 2+3+1=6 ticks. Signals arrive at ticks 6, 8, 10
        expected_output = [ 
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # Ticks 0-7
            5.0,  # Tick 8: signal from tick 0
            0.0,   # Tick 9
            5.0,   # Tick 10: signal from tick 2
        ]
        self.engine.core.load(self.pkg)
        self._run_and_assert(df_in, 'o1', expected_output)

    def test_parallel_processing(self):
        # Parallel paths with different delays:
        # Input -> N1 (L=1) -> Output1
        # Input -> N2 (L=2) -> Output2
        self.engine.tick_offset = 0
        i1 = self.pkg.new_tape_input("i1", [])
        n1 = self.pkg.new_neuron(leak=0.0, peak=3.0, receivers=[])
        n2 = self.pkg.new_neuron(leak=0.0, peak=3.0, receivers=[])
        o1 = self.pkg.new_output("o1")
        o2 = self.pkg.new_output("o2")
        
        self.pkg.new_link_between(0.0, 1, i1, n1)
        self.pkg.new_link_between(0.0, 2, i1, n2)
        self.pkg.new_link_between(0.0, 1, n1, o1)
        self.pkg.new_link_between(0.0, 1, n2, o2)
        
        # Input pattern: [3, 0, 3, 0, 3, 0]
        df_in = pd.DataFrame([3.0, 0.0, 3.0, 0.0, 3.0, 0.0], columns=['i1'])
        
        # Expected outputs:
        # o1 delay: 1+1=2 ticks, o2 delay: 2+1=3 ticks
        expected_o1 = [0.0, 0.0, 0.0, 3.0, 0.0, 3.0, 0.0]  
        expected_o2 = [0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0]  
        self.engine.core.load(self.pkg)
        cp1 = self._takeCoreCheckpoint()
        print(f"@@ first run with tick {self.engine.core.tick()}  {cp1.tick}")
        self._run_and_assert(df_in, 'o1', expected_o1, cut_expected=True)
        self._applyCoreCheckpoint(cp1)
        print(f"@@ new run with tick {self.engine.core.tick()}  {cp1.tick}")
        self._run_and_assert(df_in, 'o2', expected_o2, cut_expected=True)