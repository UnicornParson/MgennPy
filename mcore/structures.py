import uuid
import pandas as pd
from .core_object import RunnableObject, CoreObject
from common import MgennConsts, MgennComon, F, Package, RobotsLogger, ObjectIdType
from .neuron import Neuron
from .link import Link, LinkEvent
from .output import Output, OutputRecord
from .input import *
from .clock_input import *
from .errors import *




class StructsBuilder():
    def __init__(self) -> None:
        pass

    @staticmethod
    def neuron_builder(l_index:int):
        leak = 0.
        peak = 5.
        return (leak, peak)

    def make_layer(self, pkg, size, config_builder, layer_name=""):
        if size <= 1 or not config_builder:
            raise ValueError("invalid params")
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        ids = []
        for i in range(size):
            leak, peak = config_builder(i)
            id = pkg.new_neuron(leak, peak, [])
            ids.append(id)
        if not layer_name:
            layer_name = f"layer_{F.generateToken()}"

        pkg.addStructureHints({layer_name: ids})
        return (layer_name, ids, pkg)
