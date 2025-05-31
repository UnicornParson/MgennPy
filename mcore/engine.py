import pandas as pd
import time 

from enum import Enum
from .errors import *
from .core import *

class EngineCoreError(ValueError):
    def __init__(self, message="core failed"):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"EngineCoreError {self.message}"
class EngineIOError(ValueError):
    def __init__(self, message="i/o failed"):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"EngineIOError {self.message}"

class InputDataSelector():
    def select(self, in_data):
        raise NotImplementedError("implementation missed ")

class IDS_asis(InputDataSelector):
    def select(self, in_data):
        return in_data

class Engine:
    def __init__(self) -> None:
        self.core = None
        self.tick_offset = 0 # input row = tick + tick_offset

    def ready(self) -> bool:
        return bool(self.core)
    def tick(self):
        if not self.ready():
            raise ValueError("not ready")
        return self.core.tick()

    def run_once(self, input):
        if not self.core:
            raise EngineCoreError("no core")
        if not isinstance(input, pd.DataFrame):
            raise ValueError("input not a df")
        if len(input) == 0:
            raise ValueError("empty or invalid input {input}")
        if self.core.is_dirty():
            raise EngineCoreError("dirty core")
        row = TapeInputsRow(1)
        tick = self.tick()
        row_index = tick + self.tick_offset
        if len(input) <= row_index:
            raise IndexError(f"row[{row_index}] not found in input len:{len(input)} tick:{tick}")
        
        row.from_frame(input, row_index)

        self.core.update_inputs(row)
        outputs = self.core.exec()

        return outputs.data

class Rater:
    def rate(self, full_input, effective_input, tick, effective_output, ex_data = None) -> int:
        raise NotImplementedError("implementation missed ")
    def needStop(self) -> bool:
        raise NotImplementedError("implementation missed ")
    def ready(self) -> bool:
        raise NotImplementedError("implementation missed ")

"""
simple chain for external runners
"""
class RunChain:
    def __init__(self) -> None:
        self.input_selector = IDS_asis()
        self.rater = None
        self.engine = Engine()

    def check(self) -> None:
        if not self.input_selector:
            raise ValueError("no selector")
        if not self.rater:
            raise ValueError("no rater")
        if not self.engine:
            raise ValueError("no engine")
        if not self.engine.ready():
            raise ValueError("engine not ready")

    def run(self, in_data, ex_data = None) -> tuple:
        self.check()
        selected_input = self.input_selector.select(input)
        o = self.engine.run_once(selected_input)
        tick = self.engine.core.tick()
        rank = self.rater.rate(in_data, selected_input, tick, o, ex_data)
        pkg = self.engine.core.dump()
        return (pkg, rank)

class InputSource:
    def getIRow(self, tick):
        raise NotImplementedError("implementation missed ")
    def ready(self):
        raise NotImplementedError("implementation missed ")
        
class InputSourceStatic(InputSource):
    def __init__(self) -> None:
        self.tape = None
    def ready(self):
        return isinstance(self.tape, pd.DataFrame) ## tape exists
    def getIRow(self, tick):
        if not isinstance(self.tape, pd.DataFrame):
            raise ValueError("no tape (or not df)")
        if not tick in self.tape.index:
            raise IndexError(f"row {tick} not found in tape")
        return self.tape.loc[tick]
        

class OutputHandler:
    def on_output(self, tick, o):
        raise NotImplementedError("implementation missed ")
    def ready(self):
        raise NotImplementedError("implementation missed ")

class OutputHandlerNull(OutputHandler):
    """
        dev/null handler. ignore anything
    """
    def on_output(self, tick, o):
        F.print("on output[tick]")

    def ready(self):
        return True

class StorageBinder:
    def on_tick(self, tick, pkg, o, rank):
        raise NotImplementedError("implementation missed ")
    def ready(self):
        raise NotImplementedError("implementation missed ")
class StorageBinderNull:
    """
        dev/null handler. ignore anything
    """
    def on_output(self, tick, pkg, o, rank):
        pass
    def ready(self):
        return True


class CoreLifeCycle:
    class PerfKey(Enum):
        Exec = "exec"
        Store = "store"
        Output = "p_out"
        IterToral = "iter"


    def __init__(self) -> None:
        self.max_iterations = -1 # inf
        self.engine = Engine()
        self.i_source = None
        self.rater = None
        self.o_handler = OutputHandlerNull()
        self.storage_binder = None

        self.snapshots = {}
        self.perf = {}
        for key in CoreLifeCycle.PerfKey:
            self.perf[key] = []

    def ready(self) -> bool:
        return (self.engine and self.engine.ready() 
                and self.i_source and self.i_source.ready()
                and self.rater and self.rater.ready()
                and self.o_handler and self.o_handler.ready()
                and self.storage_binder and self.storage_binder.ready())

    def once(self, ex_data) -> tuple:
        if not self.ready():
            raise ValueError("not ready")
        tick = self.engine.tick()
        i = self.i_source.getIRow(tick)
        o = self.engine.run_once(i)
        rank = self.rater.rate(i, i, tick, o, ex_data)
        pkg = self.engine.core.dump()
        return (tick, pkg, o, rank)

    def full_life(self, ex_data):
        if not self.ready():
            raise ValueError("not ready")
        self.snapshots = {}
        i = 0
        life_name = F.generateMgennId()
        while True:
            iter_start = time.time()
            # 01 run
            s = time.time()
            tick, pkg, o, rank  = self.once(ex_data)
            self.perf[CoreLifeCycle.PerfKey.Exec] = float(time.time() - s)
            
            # 02 save local trace
            self.snapshots[tick] = (pkg, o, rank)

            # 03 save to storage
            s = time.time()
            self.storage_binder.on_tick(tick, pkg, o, rank)
            self.perf[CoreLifeCycle.PerfKey.Store] = float(time.time() - s)
            # 04 process outputs
            s = time.time()
            self.o_handler.on_output(tick, o)
            self.perf[CoreLifeCycle.PerfKey.Output] = float(time.time() - s)

            self.perf[CoreLifeCycle.PerfKey.IterToral] = float(time.time() - iter_start)
            if i >= self.max_iterations:
                break
            i += 1
            if self.rater.needStop():
                F.print(f"life[{life_name}] stopped by rater on tick {tick}")
                break

        for key in CoreLifeCycle.PerfKey:
            F.print(f"life[{life_name}] perf stat({CoreLifeCycle.PerfKey[key]} - {min(self.perf[key])} - {F.median(self.perf[key])} - {F.max(self.perf[key])}")


