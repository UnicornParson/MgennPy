import numpy as np
import pandas as pd
import json
import copy
import os
from .functional import F
from .mgenn_comon import MgennComon, NumpyEncoder
from .mgenn_consts import MgennConsts, ObjectIdType

class PackageUtils:
    @staticmethod
    def checkRawPkg(p: dict):
        if "meta" not in p or not p["meta"]:
            raise ValueError("no meta")
        if "content" not in p or not p["content"]:
            raise ValueError("no content")
        if "contenttype" not in p or p["contenttype"] != "json":
            raise ValueError("no contenttype")
        c = p["content"]
        meta = p["meta"]
        if "tick" not in c or np.int64(c["tick"]) < 0:
            raise ValueError("no tick")
        for req in ["generation", "history", "id", "parent", "seq", "storage", "inputs", "outputs"]:
            if req not in c:
                raise ValueError("no %s in content" % req)
        for req in ["links", "neurons"]:
            if req not in c["storage"]:
                raise ValueError("no %s in storage" % req)

        if c["parent"] != meta["parentSnapshot"]:
            raise ValueError("meta[parent] does not match with snapshot! %s != %s" % (c["parent"], meta["parentSnapshot"]))
        if c["id"] != meta["name"]:
            raise ValueError("meta[id] does not match with snapshot! %s != %s" % (c["id"], meta["name"]))

    @staticmethod
    def checkRawPkg_b(p: dict) -> bool:
        try:
            PackageUtils.checkRawPkg(p)
            return True
        except:
            return False

    def makeEmptyPkgData() -> dict:
        return {}


class Package:
    @staticmethod
    def make_empty():
        pkg = Package()
        pkg.state = "new"
        pkg.snapshot_id = MgennComon.makeId(ObjectIdType.Core)
        pkg.meta = {
            "branch":"default",
            "branchSeq": 0,
            "generation": 0,
            "name": pkg.snapshot_id,
            "parentDelta": "NONE",
            "parentSnapshot": "NONE",
            "rev": 0,
            "tick": 0
        }
        pkg.parent = "NONE"
        pkg.tick = 0
        return pkg

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

    def __contains__(self, key):
        # check string names first
        if self.findInput(key) >= 0 or self.findOutputByName(key):
            return True
        return self.isLink(key) or self.isNeuron(key) or self.isOutput(key)

    def __len__(self):
        return len(self.inputs) + len(self.outputs) + len(self.links) + len(self.neurons)

    def isValid(self, explain = False):
        if not self.state or not self.snapshot_id or not self.parent:
            if explain:
                F.print(f"required fields state:[{self.state}], snapshot_id:[{self.snapshot_id}], parent:[{self.parent}]")
            return False
        if not self.meta:
            if explain:
                F.print(f"no meta")
            return False

        if MgennComon.hasMissingKeys(self.meta, ["branch", "branchSeq", "generation", "name", "parentDelta", "parentSnapshot", "rev", "tick"]):
            if explain:
                F.print(f"missed keys in meta:{self.meta}")
            return False
        if not self.meta["name"]:
            if explain:
                F.print(f"no meta.name in meta:{self.meta}")
            return False
        if not self.meta["branch"]:
            if explain:
                F.print(f"no meta.branch in meta:{self.meta}")
            return False

        return True

    def clone(self):
        return copy.deepcopy(self)

    def empty(self)->bool:
        return self.__len__() == 0

    def removeDynamic(self):
        for n in self.neurons:
            n["currentEnergy"] = 0.0
        for l in self.links:
            l["events"] = []

    def total_energy(self) -> float:
        e = 0.0
        for n in self.neurons:
            e += float(n["currentEnergy"])
        for l in self.links:
            for event in l["events"]:
                e += float(event["finalAmplitude"])
        return e


    def introspection(self) -> tuple:
        ids = []
        values = []
        for n in self.neurons:
            ids.append(str(n["id"]))
            values.append(float(n["currentEnergy"]))
        n_df = pd.DataFrame(values, columns=ids)
        ids = []
        values = []
        for l in self.links:
            ids.append(str(n["id"]))
            for event in l["events"]:
                values.append(float(event["finalAmplitude"]))
        l_df = pd.DataFrame(values, columns=ids)
        return (n_df, l_df)


        
        

    def findLink(self, id) -> int:
        if isinstance(id, str): ## skip "find by name"
            return -1
        for i in range(len(self.links)):
            if self.links[i]['id'] == np.int64(id):
                return i
        return -1

    def findNeuron(self, id) -> int:
        if isinstance(id, str): ## skip "find by name"
            return -1
        for i in range(len(self.neurons)):
            if self.neurons[i]['id'] == np.int64(id):
                return i
        return -1

    def findOutput(self, id) -> int:
        if isinstance(id, str): ## find by name
            return self.findOutputByName(id)
        for i in range(len(self.outputs)):
            if self.outputs[i]['id'] == np.int64(id):
                return i
        return -1
    def findOutputByName(self, name) -> int:
        for i in range(len(self.outputs)):
            if self.outputs[i]['name'] == name:
                return i
        return -1
    def findInput(self, name) -> int:
        for i in range(len(self.inputs)):
            if self.inputs[i]['name'] == name:
                return i
        return -1

    def isLink(self, id) -> bool:
        return (self.findLink(id) >= 0)
    def isNeuron(self, id) -> bool:
        return (self.findNeuron(id) >= 0)
    def isOutput(self, id) -> bool:
        return (self.findOutput(id) >= 0)


    def loadFile(self, fname):
        if not os.path.isfile(fname):
            FileNotFoundError(f"pkg not founf in {fname}")
        f = open(fname)
        jstr = f.read()
        f.close()
        return self.loadJsonStr(jstr)

    def loadJsonStr(self, jstr:str):
        if not jstr:
            raise ValueError("empty json string")
        self.pkg = json.loads(jstr)
        PackageUtils.checkRawPkg(self.pkg)

        self.inputs = self.pkg["content"]["inputs"]
        self.outputs = self.pkg["content"]["outputs"]
        self.links = self.pkg["content"]["storage"]["links"]
        self.neurons = self.pkg["content"]["storage"]["neurons"]
        self.history = {}
        self.external = {}
        content = self.pkg["content"]
        self.tick =  np.int64(content["tick"])
        self.generation = int(content["generation"])
        self.seq = int(content["seq"])
        self.snapshot_id = content["id"]
        self.parent = content["parent"]
        if "state" in self.pkg:
            self.state = self.pkg["state"]
        if "meta" in self.pkg:
            self.meta = self.pkg["meta"]
        if "history" in content:
            self.history = content["history"]
        if "external" in content:
            self.external = content["external"]

        # fix types
        for i in range(0, len(self.neurons)):
            self.neurons[i]['id'] = np.int64(self.neurons[i]['id'])
            for j in range(0, len(self.neurons[i]["receivers"])):
                self.neurons[i]["receivers"][j] = np.int64(self.neurons[i]["receivers"][j])

        for i in range(0, len(self.inputs)):
            for j in range(0, len(self.inputs[i]["receivers"])):
                ##print(self.inputs[i]["receivers"])
                self.inputs[i]["receivers"][j] = np.int64(self.inputs[i]["receivers"][j])

        for i in range(0, len(self.outputs)):
            self.outputs[i]['id'] = np.int64(self.outputs[i]['id'])

        for i in range(0, len(self.links)):
            self.links[i]['id'] = np.int64(self.links[i]['id'])
            self.links[i]['receiverId'] = np.int64(self.links[i]['receiverId'])

    def dump(self):
        pkg = {}
        lastName = self.meta["name"]
        self.meta["branchSeq"] = self.meta["branchSeq"] + 1
        self.meta["parentSnapshot"] = lastName
        self.meta["name"] = self.snapshot_id
        pkgName = "%s_rev0.pkg" % self.meta["name"]

        pkg["meta"] = self.meta
        pkg["state"] = self.state
        pkg["contenttype"] = "json"

        content = {}
        content["parent"] = lastName
        content["tick"] = self.tick
        content["id"] = self.snapshot_id
        content["generation"] = self.generation
        content["seq"] = self.seq
        content["inputs"] = self.inputs
        content["outputs"] = self.outputs

        content["storage"] = {}
        content["storage"]["links"] = self.links
        content["storage"]["neurons"] = self.neurons



        content["history"] = self.history
        content["external"] = self.external
        pkg["content"] = content
        return (pkgName, pkg)

    def addStructureHints(self, hint):
        if "structs" not in self.external:
            self.external["structs"] = []
        self.external["structs"].append(hint)

    def dumpJsonStr(self):
        _, pkg = self.dump()
        return json.dumps(pkg, default=str).encode("utf-8")

    def saveToFile(self, fname = "")-> bool:
        pkgname, data = self.dump()
        if not data:
            F.print("no data!")
            return False
        if not fname:
            fname = pkgname
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, sort_keys = True, cls=NumpyEncoder)
            return True

    def counts(self):
        i = len(self.inputs)
        o = len(self.outputs)
        l = len(self.links)
        n = len(self.neurons)
        F.print(f"inputs:{i}, outputs:{o}, neurons:{l}, links:{n}, total:{(i+o+l+n)}")

    def maxId(self):
        ret = np.int64(0)
        for o in self.outputs:
            ret = max(ret, np.int64(o['id']))
        for n in self.neurons:
            ret = max(ret, np.int64(n['id']))
        for l in self.links:
            ret = max(ret, np.int64(l['id']))
        return ret

    def nextId(self):
        return self.maxId() + 1

    def linkEnds(self, link):
        link_id = int(link["id"])
        #print("looking for ", link_id)
        start = 0
        stop = np.int64(link["receiverId"])
        for n in self.neurons:
            nid = (n["id"])
            ##print(np.array(n["receivers"]))
            if link_id in np.array(n["receivers"]):
                start = np.int64(nid)
                break
        for i in self.inputs:
            iid = i["name"]
            ##print(np.array(i["receivers"]))
            if link_id == np.array(i["receivers"]):
                start = iid
                break
        if not start or not stop:
            F.print(f"link {link_id} is hanging down")
        return (start, stop)

    def connect(self, from_id, target_id)-> bool:
        if from_id  not in self:
            F.print(f"from object {from_id} not found")
            return False
        if target_id  not in self:
            F.print(f"target object {target_id} not found")
            return False

        index = self.findLink(from_id)
        if index >= 0:
            self.links[index]['receiverId'] = np.int64(target_id)
            F.print(f"linked L[{from_id}] to {target_id}")
            return True
        index = self.findNeuron(from_id)
        if index >= 0:
            if np.int64(target_id) not in self.neurons[index]["receivers"]:
                self.neurons[index]["receivers"].append(np.int64(target_id))
            F.print(f"linked N[{from_id}] to {target_id}")
            return True

        ## id can be name
        index = self.findInput(from_id)
        if index >= 0:
            if np.int64(target_id) not in self.inputs[index]["receivers"]:
                self.inputs[index]["receivers"].append(np.int64(target_id))
            F.print(f"linked I[{from_id}] to {target_id}")
            return True
        F.print(f"source object [{from_id}] not found!")
        return False

    def new_neuron(self, leak:float, peak:float, receivers:list):
        id = self.nextId()
        data = {
          "currentEnergy": 0.000000,
          "energyLeak": leak,
          "id": id,
          "mode": "shared",
          "peakEnergy": peak,
          "receivers": receivers
        }
        self.neurons.append(data)
        return id

    def new_link(self, apt:float, length:int, receiver:np.int64):
        id = self.nextId()
        data = {
          "attenuationPerTick": apt,
          "events": [],
          "id": id,
          "length": length,
          "receiverId": receiver
        }
        self.links.append(data)
        return id

    def new_link_between(self, apt:float, length:int, src:np.int64, dst:np.int64):
        lnk = self.new_link(apt, length, dst)
        self.connect(src, lnk)
        return lnk

    def new_output(self, name:str):
        for o in self.outputs:
            if o["name"] == name:
                raise ValueError(f"output name {name} already exists")
        id = self.nextId()
        data = {
          "name": name,
          "id": id,
        }
        self.outputs.append(data)
        return id

    def new_input(self, name:str, type:str, receivers:list, args:dict):
        if not name:
            raise ValueError("no input name")
        if not type:
            raise ValueError("no input type")
        for o in self.inputs:
            if o["name"] == name:
                raise ValueError(f"input name {name} already exists")

        if args == None:
            args = {}
        if receivers == None:
            receivers = []
        idata = {
            "type": type,
            "name": name,
            "receivers": receivers,
            "args": args
        }
        self.inputs.append(idata)
        return name

    def new_tape_input(self, name:str, receivers:list):
        return self.new_input(name, "tape", receivers, {})
    def new_clock_input(self, name:str, receivers:list, args:dict):
        return self.new_input(name, "clockgenerator", receivers, args)