import math
import copy
import numpy as np
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

class TapeInputsBatch(Input):
    def __init__(self):
        super().__init__()
        self.type = InputType.Tape
        self.reset()

    def addPoint(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()}")
        if data["type"] != self.type:
            raise ValueError("tape batch supports only tape points. but received")
        name = data["name"]
        receivers = data["receivers"].sort()
        ex_args = data["args"]

        if name in self.points:
            raise KeyError(f"non unic name {name}")

        self.points[name] = (receivers, ex_args)
        
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

