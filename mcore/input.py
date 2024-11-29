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

class InputComponent(Input):
    PeriodKey = "period"
    IgnoreFirstTickKey = "ignorefirst"
    AmplitudeKey = "amplitude"


    def __init__(self):
        super().__init__()
        self.__first = True
        self.reset()

    def __eq__(self, other):
        if other == None:
            return False
        return (self.period == other.period and self.ift == other.ift and self.amp == other.amp)

    def id(self):
        return 0

    def reset(self):
        self.period = 0
        self.ift = False
        self.amp = 0.
        self.__first = True
    
    def onTick(self, tick_num)->float:
        if tick_num % self.period == 0:
            if self.__first and self.ift: # ignore first
                self.__first = False
                return 0.
            self.__first = False
            return self.amp
        return 0.

    def __str__(self):
        raise f"InputComponent every {self.period} emit {self.amp} (first:{self.ift})"

    def __repr__(self):
        return self.__str__()

    def required_keys(self) -> list:
        return [InputComponent.PeriodKey, InputComponent.IgnoreFirstTickKey, InputComponent.AmplitudeKey]
    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()} expected {self.required_keys()}")
        self.reset()
        self.period = int(data[InputComponent.PeriodKey])
        self.ift = bool(data[InputComponent.IgnoreFirstTickKey])
        self.amp = float(data[InputComponent.AmplitudeKey])

    def serialize(self) -> dict:
        return {
            InputComponent.PeriodKey : self.period,
            InputComponent.IgnoreFirstTickKey : self.ift,
            InputComponent.AmplitudeKey : self.amp
        }
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
class ClockInput(Input):
    ComponentsContainerKey = "components"
    def __init__(self):
        super().__init__()
        self.type = InputType.ClockGenerator
        self.reset()
    def reset(self):
        self.name = ""
        self.receivers = []
        self.args = {}
        self.components = []

    def __eq__(self, other):
        if other == None:
            return False
        return (self.name == other.name and self.args == other.args and self.type == other.type and self.receivers.sort() == other.receivers.sort())

    def __hash__(self):
        return F.uhash(frozenset(self.serialize().items()))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def clone(self):
        return copy.deepcopy(self)
    def required_keys(self) -> list:
        return ["name", "receivers", "type", "args"]
    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()} expected {self.required_keys()}")
        if "components" not in data["args"]:
            raise KeyError(f"missed components in args. received {data['args']}")
        if data["type"] != InputType.ClockGenerator:
            raise KeyError(f"ClockInput cannot be made with data type {data['type']}")
        self.reset()
        self.name = str(data['name'])
        self.receivers = list(data["receivers"])
        c_list = data["args"]["components"]
        if not c_list or not isinstance(c_list, list):
            raise ValueError(f"invalid components of ClockInput[{self.name}]: {str(c_list)}")
        for c in c_list:
            ic = InputComponent()
            ic.deserialize(c)
            self.components.append(ic)

    def serialize(self) -> dict:
        d = {'name':self.name, "receivers": self.receivers}
        c_list = []
        for ic in self.components:
            if not ic:
                raise ValueError("null InputComponent")
            c_list.append(ic.serialize())
        d["args"] = {}
        d["args"]["components"] = c_list
        return d.sort()

    def makeEvents(self, tick_num)->list:
        amp = 0.0
        for ic in self.components:
            amp += ic.onTick(tick_num)
        if amp > 0.0:
            events = []
            for rc in self.receivers:
                events.append((rc, amp))
            return events
        return []

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

    def __eq__(self, other):
        if other == None:
            return False
        return (self.name == other.name and self.args == other.args and self.type == other.type)

    def __hash__(self):
        return F.uhash((self.name, self.args, self.type))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def clone(self):
        return copy.deepcopy(self)

    def reset(self):
        self.name = ""
        self.receivers = []
        self.args = {}
        self.points = {}

    def __str__(self):
        return f"TapeInputsBatch({self.name}. to [{self.receivers}] args {self.args})"

    def __repr__(self):
        return self.__str__()

    def id(self):
        return self.localId

