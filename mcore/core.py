import math
import copy
from .core_object import RunnableObject, CoreObject
from common import MgennConsts, MgennComon, F, Package

class Core(CoreObject):
    def __init__(self) -> None:
        super().__init__()
        pkg = None
        content = {}

    def load(self, pkg: Package):
        if not pkg:
            raise ValueError("empty pkg")
        self.pkg = pkg