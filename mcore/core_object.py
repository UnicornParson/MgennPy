import json
from common import *

class CoreRobotKeys:
    LINK_APPLY_EVENT = "LINK_APPLY_EVENT"
    OUTUT_IN = "OUTUT_IN"
    NEURON_SHOT = "NEURON_SHOT"
    NEURON_IN = "NEURON_IN"

class CoreObject:
    def __str__(self):
        raise NotImplementedError("implementation missed ")
    def __repr__(self):
        return self.__str__()
    def id(self):
        raise NotImplementedError("implementation missed ")
    def required_keys(self) -> list:
        return []
    def deserialize(self, data: dict):
        raise NotImplementedError("implementation missed ")

    def serialize(self) -> dict:
        raise NotImplementedError("implementation missed ")

    def reset(self):
        pass
    

    def onRobotsEvent(self, msg:str, args:dict):
        src = f"{type(self).__name__}.{self.id()}.{self.__hash__():x}"
        if RobotsLogger.default:
            args["oid"] = self.id()
            args["ohash"] = f"{self.id()}.{self.__hash__():}"
            RobotsLogger.default.onEvent(msg, args, src)
        #else:
        #    print(f"@ {src} {msg} : {json.dumps(args)}")


class RunnableObject(CoreObject):
    def __init__(self) -> None:
        super().__init__()
    def onTick(self, tick_num)->float:
        raise NotImplementedError("implementation missed ")
    def onSignal(self, tick_num, amplitude:float, from_id = 0):
        raise NotImplementedError("implementation missed ")
    def makeEvents(self, amp: float)->list:
        raise NotImplementedError("implementation missed ")