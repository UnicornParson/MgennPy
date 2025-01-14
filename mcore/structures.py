import uuid
import pandas as pd
import numpy as np
import itertools
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
    def neuron_builder(l_index):
        leak = 0.
        peak = 5.
        return (leak, peak)

    @staticmethod
    def link_builder(from_id, to_id):
        apt = 1.
        length = 1
        return (apt, length)

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

    @staticmethod
    def grid_to_list(grid:np.ndarray) -> list:
        return grid.flatten().tolist()


    def make_ngrid(self, pkg, shape:tuple, config_builder, layer_name=""):
        if not shape or not config_builder:
            raise ValueError("invalid params")
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        inexes = np.empty(shape)
        for i in np.ndindex(inexes.shape):
            leak, peak = config_builder(i)
            id = pkg.new_neuron(leak, peak, [])
            inexes[i] = id
        if not layer_name:
            layer_name = f"grid_{F.generateToken()}"
        pkg.addStructureHints({layer_name: inexes})
        return (layer_name, inexes, pkg)

    def connect_layers_1_1(self, pkg, l, r, link_builder):
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        if isinstance(l, np.ndarray):
            l = StructsBuilder.grid_to_list(l)
        if isinstance(r, np.ndarray):
            r = StructsBuilder.grid_to_list(r)
        if len(l) != len(r):
            raise ValueError(f"sizes not match l({len(l)}) != ({len(r)})")
        links = []
        for i in range(len(l)):
            apt, length = link_builder(l[i], r[i])
            lnk = pkg.new_link_between(apt, length, l[i], r[i])
            links.append(lnk)
        return links, pkg

    def connect_layers_all(self, pkg, l, r, link_builder):
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        if isinstance(l, np.ndarray):
            l = StructsBuilder.grid_to_list(l)
        if isinstance(r, np.ndarray):
            r = StructsBuilder.grid_to_list(r)
        links = []
        for li, ri in list(itertools.product(l, r)):
            apt, length = link_builder(li, ri)
            lnk = pkg.new_link_between(apt, length, li, ri)
            links.append(lnk)
        return links, pkg
