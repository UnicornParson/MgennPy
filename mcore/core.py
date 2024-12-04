import math
import copy
from .core_object import RunnableObject, CoreObject
from common import MgennConsts, MgennComon, F, Package, RobotsLogger
from .neuron import Neuron
from .link import Link, LinkEvent
from .output import Output
from .input import *
from .clock_input import *

class Core(CoreObject):
    def __init__(self) -> None:
        super().__init__()
        self.pkg = None
        self.content = {}
        self.itape = None
        self.autoinputs = {}
    def empty(self) -> bool:
        return not (bool(self.content) or bool(self.autoinputs) or (self.itape != None))

    def __contains__(self, key):
        return (key in self.content) or (key in self.autoinputs) or (self.itape != None and (key in self.itape))

    def __len__(self):
        return len(self.content)

    def load(self, pkg: Package):
        if not pkg:
            raise ValueError("empty pkg")
        self.pkg = pkg
        for n in pkg.neurons:
            if not isinstance(n, dict):
                raise ValueError(f"neuron {n} is not a dict")
            neuron = Neuron()
            neuron.deserialize(n)
            if neuron.id() in self.content:
                raise ValueError(f"id {neuron.id()} is not unic in this core")
            self.content[neuron.id()] = neuron
        for l in pkg.links:
            if not isinstance(l, dict):
                raise ValueError(f"link {l} is not a dict")
            link = Link()
            link.deserialize(l)
            if link.id() in self.content:
                raise ValueError(f"id {link.id()} is not unic in this core")
            self.content[link.id()] = link
        for l in pkg.outputs:
            if not isinstance(l, dict):
                raise ValueError(f"output {l} is not a dict")
            output = Output()
            output.deserialize(l)
            if output.id() in self.content:
                raise ValueError(f"output id {output.id()} is not unic in this core")
            self.content[output.id()] = output
        for i in pkg.inputs:
            if not isinstance(i, dict):
                raise ValueError(f"input {l} is not a dict")
            bi = Input()
            if MgennComon.hasMissingKeys(i, bi.required_keys()):
                raise KeyError(f"missed keys in {i.keys()} expected {bi.required_keys()}")
            it = i["type"]
            F.print(f"found input {it}")
            if it == InputType.ClockGenerator:
                ci = ClockInput()
                ci.deserialize(i)
                name = ci.name
                if name in self.autoinputs:
                    raise ValueError(f"input name {name} is not unic in this core")
                F.print(f"new ClockGenerator input {name}")
                self.autoinputs[name] = ci
            elif it == InputType.Tape:
                if self.itape == None: # firsat tape. make batch container
                    self.itape = TapeInputsBatch()
                self.itape.addPoint(i)
            elif it == InputType.Passive:
                F.print(f"ignore passive input {i['name']}")
            else:
                raise ValueError(f"input type {i['type']} is not supported")

    def neurons(self):
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Neuron):
                rc.append(obj)
        return rc

    def links(self):
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Link):
                rc.append(obj)
        return rc

    def outputs(self):
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Output):
                rc.append(obj)
        return rc

    def dump(self) -> Package:
        pkg = Package()
        pkg.generation = self.pkg.generation + 1
        pkg.seq = self.pkg.seq
        pkg.snapshot_id = MgennComon.makeId()
        pkg.parent = self.pkg.snapshot_id
        pkg.state = self.pkg.state
        pkg.tick = self.pkg.tick
        pkg.meta = copy.deepcopy(self.pkg.meta)
        pkg.history["format"] = "robots"
        pkg.history["format_ver"] = "0.1"
        pkg.history["items"] = copy.deepcopy(RobotsLogger.default.log)
        pkg.external = copy.deepcopy(self.pkg.external)
        for elem in self.content:
            data = elem.serialize()
            if isinstance(elem, Neuron):
                print("save neuron")
                pkg.neurons.append(data)
            elif isinstance(elem, Link):
                print("save neuron")
                pkg.neurons.append(data)

        self.pkg = pkg
        return pkg



'''
class Package:
    def __init__(self):
        self.pkg = {}
        self.inputs = []
        self.outputs = []
        self.links = []
        self.neurons = []
        self.state = "ready"
        self.meta = {}
        self.history = {}
        self.external = {}
        self.tick = np.int64(0)
        self.generation = 0
        self.seq = 0
        self.snapshot_id = ""
        self.parent = ""

'''