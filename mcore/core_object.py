import json
from common import *

class CoreObject:
    def __str__(self):
        raise NotImplementedError("implementation missed ")
    def __repr__(self):
        print("repr in ", type(self))
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
        if RobotsLogger.default:
            args["oid"] = self.id
            args["ohash"] = self.__hash__()
            RobotsLogger.default.onEvent(msg, args)
        else:
            print(f"@ {msg} : {json.dumps(args)}")


class RunnableObject(CoreObject):
    def onTick(self, tick_num)->float:
        raise NotImplementedError("implementation missed ")
    def onSignal(self, tick_num, amplitude:float, from_id = 0):
        raise NotImplementedError("implementation missed ")