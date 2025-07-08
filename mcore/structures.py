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

class LayerInfo():
    CONTENT_TYPE_NONE = 0
    CONTENT_TYPE_NEURONS = 1
    CONTENT_TYPE_INPUTS = 2
    CONTENT_TYPE_OUTPUTS = 3

    def __init__(self) -> None:
        self.layer_name = ""
        self.content_type = LayerInfo.CONTENT_TYPE_NONE
        self.ids_type = list
        self.ids = []
        self.shape = (0, )
        self.dims = 0

    def to_dict(self):
        d = {}
        if self.ids_type == list:
            if not isinstance(self.ids, list):
                raise ValueError(f"ids not a list (actual: {type(self.ids)}) but declared type is list")
            d["ids_type"] = "list"
            d["ids"] = self.ids
        elif self.ids_type == np.ndarray:
            if not isinstance(self.ids, np.ndarray):
                raise ValueError(f"ids not a np.ndarray (actual: {type(self.ids)}) but declared type is np.ndarray")
            d["ids"] = self.ids.tolist()
            d["ids_type"] = "np.ndarray"
        else:
            raise ValueError("invalid ids_type")
        d["content_type"] = self.content_type
        d["layer_name"] = self.layer_name
        d["dims"] = self.dims
        return d

    def from_dict(self, d):
        """
        Restore LayerInfo fields from a dictionary (e.g., after serialization).
        All required keys must be present, otherwise ValueError is raised.
        """
        required_keys = ["layer_name", "content_type", "dims", "ids_type", "ids"]
        for key in required_keys:
            if key not in d:
                raise ValueError(f"Missing required key in LayerInfo dict: '{key}'")
        self.layer_name = d["layer_name"]
        self.content_type = d["content_type"]
        self.dims = d["dims"]
        ids_type = d["ids_type"]
        if ids_type == "list":
            self.ids_type = list
            self.ids = d["ids"]
            self.shape = (len(self.ids),)
        elif ids_type == "np.ndarray":
            self.ids_type = np.ndarray
            self.ids = np.array(d["ids"], dtype=np.int64)
            self.shape = self.ids.shape
        else:
            raise ValueError(f"Unknown ids_type: {ids_type}")
        return self


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
        li = LayerInfo()
        li.ids = []
        li.ids_type = list
        li.content_type = LayerInfo.CONTENT_TYPE_NEURONS
        li.layer_name = layer_name
        li.dims = 1
        for i in range(size):
            leak, peak = config_builder(i)
            id = pkg.new_neuron(leak, peak, [])
            li.ids.append(id)
        if not li.layer_name:
            li.layer_name = f"n_layer_{F.generateToken()}"
        li.shape = (len(li.ids), )
        pkg.addStructureHints({layer_name: li.ids})
        return (li, pkg)

    @staticmethod
    def grid_to_list(grid:np.ndarray) -> list:
        if grid.dtype != np.int64:
            grid = grid.astype(np.int64)
        return grid.flatten().tolist()


    def make_ngrid(self, pkg, shape:tuple, config_builder, layer_name=""):
        if not shape or not config_builder:
            raise ValueError("invalid params")
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        li = LayerInfo()
        li.ids_type = np.ndarray
        li.content_type = LayerInfo.CONTENT_TYPE_NEURONS
        li.layer_name = layer_name
        li.ids = np.empty(shape)
        li.shape = shape
        li.dims = len(shape)
        for i in np.ndindex(li.ids.shape):
            leak, peak = config_builder(i)
            id = pkg.new_neuron(leak, peak, [])
            li.ids[i] = id
        if not layer_name:
            layer_name = f"n_grid_{F.generateToken()}"
        li.ids = li.ids.astype(np.int64)
        pkg.addStructureHints({layer_name: li.ids})
        return (li, pkg)

    def connect_layers_1_1(self, pkg, l, r, link_builder):
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        if isinstance(l, np.ndarray):
            if l.dtype != np.int64:
                l = r.astype(np.int64)
            l = StructsBuilder.grid_to_list(l)
        if isinstance(r, np.ndarray):
            if r.dtype != np.int64:
                r = r.astype(np.int64)
            r = StructsBuilder.grid_to_list(r)
        if len(l) != len(r):
            raise ValueError(f"sizes not match l({len(l)}) != ({len(r)})")
        links = []
        for i in range(len(l)):
            apt, length = link_builder(l[i], r[i])
            lnk = None
            try:
                lnk = pkg.new_link_between(apt, length, l[i], r[i])
            except Exception as e:
                F.print(f"cannot make links. grids: \n{l}\n{r}")
                raise e
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
