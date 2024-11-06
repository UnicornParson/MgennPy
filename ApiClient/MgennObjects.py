class Neuron:
    def __init__(self):
        self.localId = MgennConsts.NULL_ID
        self.currentEnergy = 0.0
        self.energyLeak = 0.0
        self.peakEnergy = 0.0
        self.mode = ""
        self.receivers = 0

    def deserialize(data):
        i = 0

    def serialize(data):
        i = 0

class Snapshot:
    def __init__(self, engine):
        self.name = MgennConsts.NULL_NAME
        self.parentName = MgennConsts.NULL_NAME
        self.deltaName = MgennConsts.NULL_NAME
        self.branchName = MgennConsts.NULL_NAME
        self.branchSeq = 0
        self.rev = 0
        self.genearation = 0
        self.tick = 0
        self.neurons = 0
        self.links = 0
        self.history = 0
        self.inputs = 0
        self.outputs = 0
        self.engine = engine

    def getList():
        print("get list")

    def load(self, name, rev = -1):
        if name == "":
            print("empty name")
            return False

        content = {defs.ApiTag.TAG_NAME: name}
        resp = self.engine.query(defs.ApiCmd.CMD_GET_SNAPSHOT, 0, content)
        if not self.engine.isResponseOk(resp):
            print("error responce:" + resp.meta.state + " comment: " + resp.meta.comment)
            return False
        respContent = resp.content

    def save(self):
        i = 0

    def clone(self):
        i = 0

    def deserialize(self, data):
        i = 0

    def serialize(self, data):
        i = 0

    def isValid(self):
        return (self.engine != 0) and (self.name != MgennConsts.NULL_NAME)