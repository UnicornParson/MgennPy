import math
import copy
import numpy as np
from .core_object import RunnableObject, CoreObject, CoreRobotKeys
from common import MgennConsts, MgennComon, F

class LinkEvent(CoreObject):
    def __init__(self):
        super().__init__()
        self.reset()

    def __eq__(self, other):
        return (self.finalAmplitude == other.finalAmplitude and self.tick == other.tick)

    def __hash__(self):
        return F.uhash((self.finalAmplitude, self.tick))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def clone(self):
        return copy.deepcopy(self)

    def reset(self):
        self.finalAmplitude = 0.
        self.tick = 0
        self.from_id = 0

    def __str__(self):
        return f"LinkEvent(from_{self.from_id}. {self.finalAmplitude} at {self.tick})"

    def __repr__(self):
        return self.__str__()

    def id(self):
        return 0

    def required_keys(self) -> list:
        return ["finalAmplitude",  "tick"]

    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()}")
        self.tick = int(data["tick"])
        self.finalAmplitude = float(data["finalAmplitude"])
        self.from_id = 0
        if "from" in data:
            self.from_id = int(data["from"])

    def serialize(self) -> dict:
        return {
            "from":self.from_id,
            "finalAmplitude":self.finalAmplitude,
            "tick":self.tick,
        }


class Link(RunnableObject):
    def __init__(self):
        super().__init__()
        self.reset()
    def clone(self):
        return copy.deepcopy(self)
    def id(self):
        return self.localId

    def reset(self):
        self.localId = MgennConsts.NULL_ID
        self.events = []
        self.apt = 0.
        self.length = 0
        self.receiverId = 0

    def __str__(self):
        return f"Link[{self.id()}](apt:{self.apt}, l:{self.length} to:{self.receiverId} events:{len(self.events)})"

    def __hash__(self):
        return F.uhash((self.apt, self.length, self.receiverId, frozenset(self.events)))

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False
        return (self.apt == other.apt and
                self.length == other.length and
                self.receiverId == other.receiverId and
                self.events.sort() == other.events.sort())

    def id(self):
        return self.localId

    def required_keys(self) -> list:
        return ["attenuationPerTick", "events", "length", "receiverId"]

    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()} expected {self.required_keys()}")
        self.reset()
        self.apt = float(data["attenuationPerTick"])
        self.length = int(data["length"])
        self.receiverId = int(data["receiverId"])
        if 'id' in data:
            self.localId = np.int64(data['id'])
        for e in data["events"]:
            if not isinstance(e, dict):
                raise ValueError(f"event {e} is not a dict")
            le = LinkEvent()
            le.deserialize(e)
            self.events.append(le)


    def serialize(self) -> dict:
        d = {
            'id': self.localId,
            "attenuationPerTick":self.apt,
            "length":self.length,
            "receiverId":self.receiverId,
            "events": []
        }
        for e in self.events:
            d["events"].append(e.serialize())
        return d
        
    def onTick(self, tick_num)->float:
        amp = 0.0
        filtered = []
        for e in self.events:
            if e.tick <= tick_num:
                amp += e.finalAmplitude
                self.onRobotsEvent(CoreRobotKeys.LINK_APPLY_EVENT, {"tick":e.tick, "amp":e.finalAmplitude, "from": e.from_id})
            else:
                filtered.append(e)
        self.events = filtered
        return amp

    def onSignal(self, tick_num, amplitude:float, from_id = 0):
        e = LinkEvent()
        e.finalAmplitude = amplitude - (self.apt * float(self.length))
        if e.finalAmplitude <= 0.0:
            self.onRobotsEvent("LINK_IGNORE_SIGNAL", {"tick":tick_num, "amp":amplitude, "from": from_id})
            return
        e.tick = tick_num + self.length
        e.from_id = from_id
        self.events.append(e)