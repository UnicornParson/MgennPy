import math

from .core_object import RunnableObject
from common import MgennConsts, MgennComon

class Link(RunnableObject):
    def __init__(self):
        super().__init__()
        self.reset()

    def id(self):
        return self.localId
    def reset(self):
        self.localId = MgennConsts.NULL_ID