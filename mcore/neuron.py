import math
import copy
from .core_object import RunnableObject
from common import MgennConsts, MgennComon

class Neuron(RunnableObject):
    def __init__(self):
        super().__init__()
        self.reset()

    def id(self):
        return self.localId

    def reset(self):
        self.localId = MgennConsts.NULL_ID
        self.currentEnergy = 0.0
        self.energyLeak = 0.0
        self.peakEnergy = 0.0
        self.mode = ""
        self.receivers = 0

    def required_keys(self) -> list:
        return ["currentEnergy", "energyLeak", "mode", "peakEnergy", "receivers"]

    def clone(self):
        return copy.deepcopy(self)

    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()}")
        self.currentEnergy = float(data["currentEnergy"])
        self.energyLeak = float(data["energyLeak"])
        self.peakEnergy = float(data["peakEnergy"])
        self.mode = str(data["mode"])
        self.receivers = list(data["receivers"])

    def serialize(self) -> dict:
        return {
            "currentEnergy": self.currentEnergy,
            "energyLeak": self.energyLeak,
            "mode": self.mode,
            "peakEnergy": self.peakEnergy,
            "receivers": self.receivers
        }
    def __eq__(self, other):
        return (self.currentEnergy == other.currentEnergy and
                self.energyLeak == other.energyLeak and
                self.mode == other.mode and
                self.receivers.sort() == other.receivers.sort())

    def __str__(self):
        return f"N[{self.localId}]e:{self.currentEnergy} l:{self.energyLeak} p:{self.peakEnergy}"

    def onTick(self, tick_num)->float:
        if self.currentEnergy > self.peakEnergy or math.isclose(self.currentEnergy, self.peakEnergy):
            shot_energy = self.currentEnergy
            self.currentEnergy = 0.0
            self.onRobotsEvent("NEURON_SHOT", {"tick":tick_num, "amp":shot_energy})
            return MgennComon.mround(shot_energy)
        self.currentEnergy -= MgennComon.mround(self.energyLeak)
        if self.currentEnergy < 0.0:
            self.currentEnergy = 0.0
        return 0.0

    def onSignal(self, tick_num, amplitude:float, from_id = 0):
        self.onRobotsEvent("NEURON_IN", {"tick":tick_num, "amp":amplitude, "from": from_id})
        self.currentEnergy += MgennComon.mround(amplitude)

