import copy
import numpy as np
from .core_object import RunnableObject, CoreRobotKeys
from common import MgennConsts, MgennComon, F

class Output(RunnableObject):
    def __init__(self):
        super().__init__()
        self.reset()

    def clone(self):
        return copy.deepcopy(self)
    def id(self):
        return self.localId

    def reset(self):
        self.localId = MgennConsts.NULL_ID
        self.name = ""
        self.value = 0.

    def __str__(self):
        return f"Output[{self.id()}]( name:{self.name}, value:{self.value} )"

    def __hash__(self):
        return F.uhash((self.name,))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False
        return (self.name == other.name) and (self.localId == other.localId)

    def id(self):
        return self.localId

    def required_keys(self) -> list:
        return ["id", "name"]

    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()} expected {self.required_keys()}")
        self.reset()
        self.name = str(data["name"])
        self.localId = np.int64(data['id'])

    def serialize(self) -> dict:
        return {"id": self.localId, "name": self.name}

    def onTick(self, tick_num)->float:
        amp = self.value
        self.value = 0.
        return amp

    def onSignal(self, tick_num, amplitude:float, from_id = 0):
        self.onRobotsEvent(CoreRobotKeys.OUTUT_IN, {"tick":tick_num, "amp":amplitude, "from": from_id})
        self.value += amplitude