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

class RunnableObject(CoreObject):
    def onTick(self, tick_num):
        raise NotImplementedError("implementation missed ")
    def onSignal(self, tick_num, amplitude:float):
        raise NotImplementedError("implementation missed ")