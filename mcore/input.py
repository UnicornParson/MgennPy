import math
import copy
import numpy as np
import pandas as pd

from .core_object import RunnableObject, CoreObject, CoreRobotKeys
from common import MgennConsts, MgennComon, F

class InputType():
    Passive = "passive"
    ClockGenerator = "clockgenerator"
    RandomGenerator = "randomgenerator"
    Manual = "manual"
    Tape = "tape"

class Input(CoreObject):
    def __init__(self) -> None:
        super().__init__()
        self.type = ""
    def makeEvents(self, tick_num)->list:
        raise NotImplementedError("implementation missed ")
    def required_keys(self) -> list:
        return ["name",  "type", "receivers", "args"]

'''
      {
        "type": "tape",
        "name": "Alias1",
        "receivers": [11],
        "args": {
          "components": []
        }
      },

      namespace InputTypeStr

'''

## point format {name: (receivers, args)}
## args not used but should be restored asis
class TapeInputsRow():
    def __init__(self, size:int, dtype=float):
        if size < 1:
            raise ValueError(f"invalid row size {size}")
        self.data = np.zeros(size, dtype=dtype)
        self.headers = []

    def from_frame(self, df:pd.DataFrame, row_index = 0):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("input not a df")
        if len(df) <= row_index:
            raise ValueError(f"no row {row_index} in data frame")
        self.headers = df.columns.tolist()
        self.data = df.iloc[row_index].to_numpy()
        if not self.is_valid():
            raise ValueError("invalid dataframe")
    def dprint(self):
       F.print(self.__str__())
    def is_valid(self) -> bool:
        self.dprint()
        return (len(self.headers) == self.data.size) and (np.ndim(self.data) == 1)
    def is_empty(self) -> bool:
        return (self.data.size == 0)
    def value(self, name:str):
        if self.is_empty():
            return 0
        if not self.is_valid():
            raise ValueError(f"invalid row {self.__str__()}")
        if name not in self.headers:
            raise IndexError(f"{name} not found in row")
        i = self.headers.index(name)
        return self.data[i]
    def __str__(self):
        return f"TapeInputsRow h[{len(self.headers)}], d[s{self.data.size}.dim{np.ndim(self.data)}]"
    def __repr__(self):
        return self.__str__()

        
class TapeInputsBatch(Input):
    def __init__(self):
        super().__init__()
        self.type = InputType.Tape
        self.reset()
        self.__row = None


    def addPoint(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()}")
        if data["type"] != self.type:
            raise ValueError("tape batch supports only tape points. but received")
        name = data["name"]
        receivers = list(data['receivers'])
        ex_args = data["args"]

        if name in self.points:
            raise KeyError(f"non unic name {name}")

        F.print(f"store point {name} : r:{receivers} ex: {ex_args} data:{data}")
        self.points[name] = (receivers, ex_args)
    
    def updateRow(self, row):
        if not row.is_valid():
            raise ValueError("invalid row")
        self.__row = row

    def makeEvents(self, tick_num)->list:
        if not self.__row or not self.__row.is_valid():
            raise NoDataException("core row", "invalid row")
        events = []
        for name in self.points:
            if name not in self.__row.headers:
                raise IndexError(f"name {name} not found in row {self.__row.headers}")
            receivers = self.points[name][0]
            F.print(f"proces point [{name}] : {self.points[name]}")
            val = self.__row.value(name)
            for r in receivers:
                events.append((r, val, name))
        return events

    def point_names(self) -> list:
        return list(self.points.keys())

    def dump(self) -> list:
        l = []
        for name, point in self.points.items():
            receivers, ex_args = point
            i_data = {
                "name": name,
                "type": self.type,
                "receivers": receivers,
                "args": ex_args
            }
            l.append(i_data)
        return l


        
    def __contains__(self, key):
        return (key in self.points)

    def __len__(self):
        return len(self.points)
        
    def __eq__(self, other):
        if other == None:
            return False
        return (F.d_eq(self.points, other.points))

    def __hash__(self):
        return F.uhash(frozenset(self.points.keys().items()))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def clone(self):
        return copy.deepcopy(self)

    def reset(self):
        self.points = {}

    def __str__(self):
        return f"TapeInputsBatch({len(self.points)} points)"

    def __repr__(self):
        return self.__str__()

    def id(self):
        return 0

