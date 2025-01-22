import math
import copy
import pandas as pd
from .core_object import RunnableObject, CoreObject
from common import MgennConsts, MgennComon, F, Package, RobotsLogger, ObjectIdType
from .neuron import Neuron
from .link import Link, LinkEvent
from .output import Output, OutputRecord
from .input import *
from .clock_input import *
from .errors import *

class Core(CoreObject):
    """
    Represents a core in the MGenn framework, which is responsible for managing 
    neurons, links and outputs. It also handles auto-inputs and tape inputs.
    
    Attributes:
    pkg (Package): The package associated with this core.
    content (dict): A dictionary of objects in this core, including neurons, links and outputs.
    itape (TapeInputsBatch or None): A batch container for tape inputs.
    autoinputs (dict): A dictionary of auto-inputs.
    pending_events (list): A list of events that need to be processed.
    """

    def __init__(self) -> None:
        """
        Initializes a new Core object.
        
        Creates a default package and sets up the core's content, itape and autoinputs.
        """
        super().__init__()
        self.pkg = None
        self.content = {}
        self.itape = None
        self.autoinputs = {}
        if not RobotsLogger.default:
            RobotsLogger.default = RobotsLogger()
        self.pending_events = []

    def empty(self) -> bool:
        """
        Checks if this core is empty.
        
        Returns:
        bool: True if the core is empty, False otherwise.
        """
        return not (bool(self.content) or bool(self.autoinputs) or (self.itape != None))

    def is_dirty(self)->bool:
        """
        Checks if there are any dirty events in this core.
        
        Returns:
        bool: True if there are dirty events, False otherwise.
        """
        return bool(self.pending_events)

    def __contains__(self, key):
        """
        Checks if a key is present in the core's content or autoinputs.
        
        Args:
        key (str): The key to check for.
        
        Returns:
        bool: True if the key is found, False otherwise.
        """
        return (key in self.content) or (key in self.autoinputs) or (self.itape != None and (key in self.itape))

    def __len__(self):
        """
        Gets the number of objects in this core's content.
        
        Returns:
        int: The number of objects.
        """
        return len(self.content)

    def total_energy(self) -> float:
        """
        Calculates the total energy of all objects in this core.
        
        Returns:
        float: The total energy.
        """
        e = 0.0
        for item in self.content.values():
            e += item.total_energy()
        return e

    def removeDynamic(self):
        """
        Removes dynamic items from the core's content.
        """
        for item in self.content.values():
            item.removeDynamic()

    def load(self, pkg: Package):
        """
        Loads a package into this core.
        
        Args:
        pkg (Package): The package to load.
        
        Raises:
        ValueError: If the package is empty.
        """
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
        """
        Gets the list of neurons in this core.
        
        Returns:
        list: The list of neurons.
        """
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Neuron):
                rc.append(obj)
        return rc

    def links(self):
        """
        Gets the list of links in this core.
        
        Returns:
        list: The list of links.
        """
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Link):
                rc.append(obj)
        return rc

    def outputs(self):
        """
        Gets the list of outputs in this core.
        
        Returns:
        list: The list of outputs.
        """
        rc = []
        for obj in self.content.values():
            if isinstance(obj, Output):
                rc.append(obj)
        return rc
    
    def autoinputs(self):
        """
        Gets the dictionary of auto-inputs.
        
        Returns:
        dict: The dictionary of auto-inputs.
        """
        return copy.deepcopy(self.autoinputs.values())

    def dump(self, explain = False) -> Package:
        """
        Dumps the state of this core into a package.
        
        Args:
        explain (bool): If True, prints explanations for each object being dumped. Defaults to False.
        
        Returns:
        Package: The package containing the state of this core.
        """
        if not self.pkg:
            self.pkg = Package.make_empty()
        pkg = Package()
        pkg.generation = self.pkg.generation + 1
        pkg.seq = self.pkg.seq
        pkg.snapshot_id = MgennComon.makeId(ObjectIdType.Core)
        pkg.parent = self.pkg.snapshot_id
        pkg.state = self.pkg.state
        pkg.tick = self.pkg.tick
        pkg.meta = copy.deepcopy(self.pkg.meta)
        pkg.history["format"] = "robots"
        pkg.history["format_ver"] = "0.1"
        pkg.history["items"] = copy.deepcopy(RobotsLogger.default.log)
        pkg.external = copy.deepcopy(self.pkg.external)
        for id, elem in self.content.items():
            data = elem.serialize()
            if isinstance(elem, Neuron):
                if explain:
                    F.print(f"save neuron {id}")
                pkg.neurons.append(data)
            elif isinstance(elem, Link):
                if explain:
                    F.print(f"save link {id}")
                pkg.links.append(data)
            elif isinstance(elem, Output):
                if explain:
                    F.print(f"save output {id}")
                pkg.outputs.append(data)
        for ai in self.autoinputs.values():
            pkg.inputs.append(ai.serialize())
        if explain:
            F.print(f"p1 inputs len {len(pkg.inputs)}")
        if self.itape:
            pkg.inputs.extend(self.itape.dump())
        if explain:
            F.print(f"p2 inputs len {len(pkg.inputs)}")
        self.pkg = pkg
        return pkg

    def input_names(self) -> list:
        """
        Gets the list of input names in this core.
        
        Returns:
        list: The list of input names.
        """
        if self.itape:
            return self.itape.point_names()
        return []

    def update_inputs(self, row):
        """
        Updates the input at the specified row index.
        
        Args:
        row (int): The row index to update.
        """
        if self.itape:
            self.itape.updateRow(row)

    def __process_autoinputs(self):
        count_before = len(self.pending_events)
        for ai in self.autoinputs:
            self.pending_events.extend(ai.makeEvents(self.pkg.tick))
        F.print(f"autoinputs made {len(self.pending_events) - count_before} new events")

    def __process_tapes(self):
        if not self.itape:
            return
        count_before = len(self.pending_events)
        self.pending_events.extend(self.itape.makeEvents(self.pkg.tick))
        F.print(f"tape container made {len(self.pending_events) - count_before} new events")
    def __process_content(self):
        count_before = len(self.pending_events)
        for e in self.content.values():
            amp = e.onTick(self.pkg.tick)
            self.pending_events.extend(e.makeEvents(amp))
        F.print(f"active content ({len(self.content)} objects) made {len(self.pending_events) - count_before} new events")

    def __process_events(self):
        events = self.pending_events
        self.pending_events = []
        for target, amp, from_id in events:

            if target not in self.content:
                raise ConnectivityError(f"({target} is not a valid target)")
            if not self.content[target]:
                raise BrokenObject(f"invalid object {target}")
            F.print(f"process p.event {from_id}->{type(self.content[target]).__name__}_{target} amp:{amp}")
            self.content[target].onSignal(self.pkg.tick, amp, from_id)

    def __extract_outputs(self) -> OutputRecord:
        record = OutputRecord()
        headers = []
        values = []
        for o in self.outputs():
            headers.append(o.name)
            values.append(o.value)
        record.data = pd.DataFrame(data = [values,], index = [str(self.pkg.tick)], columns=headers)
        return record

    def tick(self):
        """
        Gets the current tick value.
        
        Returns:
        int: The current tick value.
        """
        if self.pkg:
            return self.pkg.tick
        return 0

    def exec(self) -> OutputRecord:
        """
        Executes this core and returns an OutputRecord.
        
        Returns:
        OutputRecord: The executed output record.
        """
        if self.empty():
            raise ValueError("empty core")
        if self.is_dirty():
            raise DirtyObjectException(who = f"core_{self.__hash__}",
                                       oid = self.pkg.snapshot_id,
                                       message = f"core is ditry. has {len(self.pending_events)} pending events")
        self.pkg.tick += 1
        self.__process_autoinputs()
        self.__process_tapes()
        self.__process_content()
        while(self.pending_events):
            self.__process_events()
        record = self.__extract_outputs()

        return record

    def max_id(self):
        """
        Gets the maximum ID in this core.
        
        Returns:
        int: The maximum ID.
        """
        return max(self.content.keys())

    def next_id(self):
        """
        Generates the next available ID for a new object in this core.
        
        Returns:
        int: The next available ID.
        """
        return self.max_id() + 1
