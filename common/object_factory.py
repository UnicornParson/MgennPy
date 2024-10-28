from . import MgennComon
import numpy as np

class ObjectFactory:
    @staticmethod
    def makeNeuronData(peak: float, leak: float, currentEnergy: float = 0, id: np.int64 = 0, receivers: list = []):
        n = {
            "currentEnergy": currentEnergy,
            "energyLeak": leak,
            "mode": "shared",
            "peakEnergy": peak,
            "receivers": []
        }
        for rids in receivers:
            n["receivers"].append(np.int64(rids))
        if id == 0:
            id = MgennComon.getLocalId()
            
        n["id"] = id
        return n
