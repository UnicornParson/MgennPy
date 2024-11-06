import math

from .core_object import CoreObject, RunnableObject
from common import MgennConsts, MgennComon

class Neuron(RunnableObject):
    def __init__(self):
        super().__init__()
        self.localId = MgennConsts.NULL_ID
        self.currentEnergy = 0.0
        self.energyLeak = 0.0
        self.peakEnergy = 0.0
        self.mode = ""
        self.receivers = 0

    def id(self):
        return self.localId

    def required_keys(self) -> list:
        return ["currentEnergy", "energyLeak", "mode", "peakEnergy", "receivers"]
        
    def deserialize(self, data: dict):
        if MgennComon.hasMissingKeys(data, self.required_keys()):
            raise KeyError(f"missed keys in {data.keys()}")
        '''
                n = {
            "currentEnergy": currentEnergy,
            "energyLeak": leak,
            "mode": "shared",
            "peakEnergy": peak,
            "receivers": []
        }
        '''
        self.currentEnergy = float(data["currentEnergy"])
        self.energyLeak = float(data["energyLeak"])
        self.peakEnergy = float(data["peakEnergy"])
        self.mode = str(data["mode"])
        self.receivers = list(data["receivers"])

    def serialize(self) -> dict:
        raise NotImplementedError("implementation missed ")

    def __str__(self):
        return f"N[{self.localId}]e:{self.currentEnergy} l:{self.energyLeak} p:{self.peakEnergy}"
    
    def onTick(self, tick_num)->float:
        if self.currentEnergy > self.peakEnergy or math.isclose(self.currentEnergy, self.peakEnergy):
            print(f"{self} shots!")
            shot_energy = self.currentEnergy
            self.currentEnergy = 0.0
            return MgennComon.mround(shot_energy)
        self.currentEnergy -= MgennComon.mround(self.energyLeak)
        if self.currentEnergy < 0.0:
            self.currentEnergy = 0.0
        return 0.0
    
    def onSignal(self, tick_num, amplitude:float):
        self.currentEnergy += MgennComon.mround(amplitude)

