import pandas as pd

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
        tick = self.core.tick()
        row_index = tick + self.tick_offset
        if len(input) <= row_index:
            raise IndexError(f"row[{row_index} not found in input len:{len(input)}")
        
        row.from_frame(input, row_index)

        self.core.update_inputs(row)
        outputs = self.core.exec()

        return outputs.data

class Rater:
    def rate(self, full_input, effective_input, tick, effective_output, ex_data = None) -> int:
        raise NotImplementedError("implementation missed ")

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
        rank = self.rater.rate(in_data, in_data, selected_input, tick, o, ex_data)
        pkg = self.engine.core.dump()
        return (pkg, rank)