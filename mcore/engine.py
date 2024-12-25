import pandas as pd

from .errors import *
from .core import *

class EngineCoreError(ValueError):
    def __init__(self, message="core failed"):
        super().__init__(self.message)
        self.message = message
    def __str__(self):
        return f"EngineCoreError {self.message}"
class EngineIOError(ValueError):
    def __init__(self, message="i/o failed"):
        super().__init__(self.message)
        self.message = message
    def __str__(self):
        return f"EngineIOError {self.message}"

class Engine:
    def __init__(self) -> None:
        self.core = None
        self.tick_offset = 0 # input row = tick + tick_offset

    def run_once(self, input:pd.DataFrame):
        if not self.core:
            raise EngineCoreError("no core")

        if self.core.is_dirty():
            raise EngineCoreError("dirty core")
        row = TapeInputsRow(1)
        tick = self.core.tick()
        row_index = tick + self.tick_offset
        row.from_frame(input, row_index)

        self.core.update_inputs(row)
        outputs = self.core.exec()

        return outputs.data