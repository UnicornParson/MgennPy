import numpy as np
import json
import copy

class PackageUtils:
    @staticmethod
    def checkPkg(p: dict):
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
        print("pkg ok")


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

    def __contains__(self, key):
        return self.isLink(key) or self.isNeuron(key) or self.isOutput(key)

    def __len__(self):
        return len(self.inputs) + len(self.outputs) + len(self.links) + len(self.neurons)

    def clone(self):
        return copy.deepcopy(self)

    def empty(self)->bool:
        return bool(self.inputs) and bool(self.outputs) and bool(self.links) and bool(self.neurons)

    def findLink(self, id) -> int:
        for i in range(len(self.links)):
            if self.links[i]['id'] == np.int64(id):
                return i
        return -1

    def findNeuron(self, id) -> int:
        for i in range(len(self.neurons)):
            if self.neurons[i]['id'] == np.int64(id):
                return i
        return -1

    def findOutput(self, id) -> int:
        for i in range(len(self.neurons)):
            if self.neurons[i]['id'] == np.int64(id):
                return i
        return -1

    def findInput(self, name) -> int:
        for i in range(len(self.inputs)):
            if self.inputs[i]['id'] == name:
                return i
        return -1

    def isLink(self, id) -> bool:
        return (self.findLink(id) >= 0)
    def isNeuron(self, id) -> bool:
        return (self.findNeuron(id) >= 0)
    def isOutput(self, id) -> bool:
        return (self.findOutput(id) >= 0)

    def loadFile(self, fname):
        f = open(fname)
        self.pkg = json.load(f)
        f.close()
        PackageUtils.checkPkg(self.pkg)

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

    def saveToFile(self, fname = "")-> bool:
        pkgname, data = self.dump()
        if not data:
            print("no data!")
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
        print("inputs:%d, outputs:%d, neurons:%d, links:%d, total:%d" % (i,o,l,n, (i+o+l+n)))

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
            print("link %d is hanging down" % link_id)
        return (start, stop)

    def connect(self, from_id, target_id)-> bool:
        if from_id  not in self:
            print("from object %d not found" % from_id)
            return False
        if target_id  not in self:
            print("target object %d not found" % from_id)
            return False

        index = self.findLink(from_id)
        if index >= 0:
            self.links[index]['receiverId'] = np.int64(target_id)
            print("linked L[%d] to %d" % (from_id, target_id ))
            return True
        index = self.findNeuron(from_id)
        if index >= 0:
            if np.int64(target_id) not in self.neurons[index]["receivers"]:
                self.neurons[index]["receivers"].append(np.int64(target_id))
            print("linked N[%d] to %d" % (from_id, target_id))
            return True

        ## id can be name
        index = self.findInput(from_id)
        if index >= 0:
            if np.int64(target_id) not in self.inputs[index]["receivers"]:
                self.inputs[index]["receivers"].append(np.int64(target_id))
            print("linked I[%d] to %d" % (from_id, target_id))
            return True
        print("source object [%s] not found!" % str(from_id))
        return False