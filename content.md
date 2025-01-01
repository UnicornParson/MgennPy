 + def random_id(length):
 + def generateToken():
 + def getNodeName():
 + def generateMgennId():
# class cmdExecutor:
 + def __init__(self, cfg):
 + def isValisCommand(self, cmd):
 + def execCmd(self, cmd, args):
 + def printHelp(self):
 + def onShow(self, args):
 + def onList(self, args):
# class RobotsLogger():
 + def __init__(self) -> None:
 + def clean(self):
 + def onEvent(self, msg:str, args:dict, src:str):
 + def print(self):
 + def __str__(self):
# class ObjectFactory:
 + def makeNeuronData(peak: float, leak: float, currentEnergy: float = 0, id: np.int64 = 0, receivers: list = []):
# class MgennConsts:
# class ObjectIdType(Enum):
# class PackageUtils:
 + def checkRawPkg(p: dict):
 + def checkRawPkg_b(p: dict) -> bool:
 + def makeEmptyPkgData() -> dict:
# class Package:
 + def make_empty():
 + def __init__(self):
 + def __contains__(self, key):
 + def __len__(self):
 + def isValid(self, explain = False):
 + def clone(self):
 + def empty(self)->bool:
 + def findLink(self, id) -> int:
 + def findNeuron(self, id) -> int:
 + def findOutput(self, id) -> int:
 + def findInput(self, name) -> int:
 + def isLink(self, id) -> bool:
 + def isNeuron(self, id) -> bool:
 + def isOutput(self, id) -> bool:
 + def loadFile(self, fname):
 + def dump(self):
 + def saveToFile(self, fname = "")-> bool:
 + def counts(self):
 + def maxId(self):
 + def nextId(self):
 + def linkEnds(self, link):
 + def connect(self, from_id, target_id)-> bool:
 + def new_neuron(self, leak:float, peak:float, receivers:list):
 + def new_link(self, apt:float, length:int, receiver:np.int64):
 + def new_output(self, name:str):
# class ApiTag:
# class ApiValus:
# class ApiRespState:
# class ApiCmd:
# class ApiAdminCmd:
# class BlState:
# class ListFilter:
# class ListFilterMod:
# class SnapshotState:
# class NumpyEncoder(json.JSONEncoder):
 + def default(self, obj):
# class MgennComon:
 + def getNodeName():
 + def getLocalId():
 + def makeId(objPrefix: str):
 + def mround(num):
 + def hasMissingKeys(dictionary: dict, keys: list) -> bool:
# class F():
 + def here_str():
 + def print(*args, **kwargs):
 + def uhash(data):
 + def random_id(length):
 + def generateToken():
 + def dsort(x:dict) -> dict:
 + def d_eq(a:dict, b:dict, maybe_none=False):
 + def dsort_val(x:dict) -> dict:
 + def getNodeName():
 + def generateOID() -> int:
 + def generateMgennId() -> str:
# class Snapshot:
 + def __init__(self, engine):
 + def getList():
 + def load(self, name, rev = -1):
 + def save(self):
 + def clone(self):
 + def deserialize(self, data):
 + def serialize(self, data):
 + def isValid(self):
# class ApiAdminHelper:
 + def __init__(self, engine):
 + def getSnapshotNames(self):
# class EngineCoreError(ValueError):
 + def __init__(self, message="core failed"):
 + def __str__(self):
# class EngineIOError(ValueError):
 + def __init__(self, message="i/o failed"):
 + def __str__(self):
# class Engine:
 + def __init__(self) -> None:
 + def run_once(self, input:pd.DataFrame):
# class InputComponent(Input):
 + def __init__(self):
 + def __eq__(self, other):
 + def id(self):
 + def reset(self):
 + def onTick(self, tick_num)->float:
 + def __str__(self):
 + def __repr__(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
# class ClockInput(Input):
 + def __init__(self):
 + def reset(self):
 + def __eq__(self, other):
 + def __hash__(self):
 + def __lt__(self, other):
 + def clone(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
 + def makeEvents(self, tick_num)->list:
# class InputType():
# class Input(CoreObject):
 + def __init__(self) -> None:
 + def makeEvents(self, tick_num)->list:
 + def required_keys(self) -> list:
# class TapeInputsRow():
 + def __init__(self, size:int, dtype=float):
 + def from_frame(self, df:pd.DataFrame, row_index = 0):
 + def dprint(self):
 + def is_valid(self) -> bool:
 + def is_empty(self) -> bool:
 + def value(self, name:str):
 + def __str__(self):
 + def __repr__(self):
# class TapeInputsBatch(Input):
 + def __init__(self):
 + def addPoint(self, data: dict):
 + def updateRow(self, row):
 + def makeEvents(self, tick_num)->list:
 + def point_names(self) -> list:
 + def __contains__(self, key):
 + def __len__(self):
 + def __eq__(self, other):
 + def __hash__(self):
 + def __lt__(self, other):
 + def clone(self):
 + def reset(self):
 + def __str__(self):
 + def __repr__(self):
 + def id(self):
# class LinkEvent(CoreObject):
 + def __init__(self):
 + def __eq__(self, other):
 + def __hash__(self):
 + def __lt__(self, other):
 + def clone(self):
 + def reset(self):
 + def __str__(self):
 + def __repr__(self):
 + def id(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
# class Link(RunnableObject):
 + def __init__(self):
 + def clone(self):
 + def id(self):
 + def reset(self):
 + def makeEvents(self, amp: float)->list:
 + def __str__(self):
 + def __hash__(self):
 + def __lt__(self, other):
 + def __repr__(self):
 + def __eq__(self, other):
 + def id(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
 + def onTick(self, tick_num)->float:
 + def onSignal(self, tick_num, amplitude:float, from_id = 0):
# class Neuron(RunnableObject):
 + def __init__(self):
 + def id(self):
 + def reset(self):
 + def makeEvents(self, amp: float)->list:
 + def required_keys(self) -> list:
 + def clone(self):
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
 + def __eq__(self, other):
 + def __hash__(self):
 + def __str__(self):
 + def onTick(self, tick_num)->float:
 + def onSignal(self, tick_num, amplitude:float, from_id = 0):
# class OutputRecord:
 + def __init__(self) -> None:
# class Output(RunnableObject):
 + def __init__(self):
 + def clone(self):
 + def id(self):
 + def makeEvents(self, amp: float)->list:
 + def reset(self):
 + def __str__(self):
 + def __hash__(self):
 + def __lt__(self, other):
 + def __repr__(self):
 + def __eq__(self, other):
 + def id(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
 + def onTick(self, tick_num)->float:
 + def onSignal(self, tick_num, amplitude:float, from_id = 0):
# class CoreRobotKeys:
# class CoreObject:
 + def __str__(self):
 + def __repr__(self):
 + def id(self):
 + def required_keys(self) -> list:
 + def deserialize(self, data: dict):
 + def serialize(self) -> dict:
 + def reset(self):
 + def onRobotsEvent(self, msg:str, args:dict):
# class RunnableObject(CoreObject):
 + def __init__(self) -> None:
 + def onTick(self, tick_num)->float:
 + def onSignal(self, tick_num, amplitude:float, from_id = 0):
 + def makeEvents(self, amp: float)->list:
# class DirtyObjectException(Exception):
 + def __init__(self, who:str, oid, message="object is dirty"):
 + def __str__(self):
# class NoDataException(ValueError):
 + def __init__(self, who:str, message="object is dirty"):
 + def __str__(self):
# class ConnectivityError(Exception):
 + def __init__(self, message=""):
 + def __str__(self):
# class BrokenObject(Exception):
 + def __init__(self, message=""):
 + def __str__(self):
# class Core(CoreObject):
 + def __init__(self) -> None:
 + def empty(self) -> bool:
 + def is_dirty(self)->bool:
 + def __contains__(self, key):
 + def __len__(self):
 + def load(self, pkg: Package):
 + def neurons(self):
 + def links(self):
 + def outputs(self):
 + def autoinputs(self):
 + def dump(self) -> Package:
 + def input_names(self) -> list:
 + def update_inputs(self, row):
 + def __process_autoinputs(self):
 + def __process_tapes(self):
 + def __process_content(self):
 + def __process_events(self):
 + def __extract_outputs(self) -> OutputRecord:
 + def tick(self):
 + def exec(self) -> OutputRecord:
 + def max_id(self):
 + def next_id(self):
# class Engine:
 + def __init__(self, apiUrl):
 + def start(self):
 + def query(self, cmd = "", args = 0, content = 0):
 + def isResponseOk(self, resp):
 + def getSnapshotList(self, filter = ""):
 + def getAlias(self, name):
# class ApiRequest:
 + def __init__(self, cmd = "", args = 0, content = 0):
# class ApiResponceMeta:
 + def __init__(self):
 + def load(self, respMataObject):
# class ApiResponce:
 + def __init__(self):
 + def load(self, respObject):
# class ApiClient:
 + def __init__(self, apiUrl):
 + def encondeContent(self, content):
 + def query(self, request):
# class Neuron:
 + def __init__(self):
 + def deserialize(data):
 + def serialize(data):
# class Snapshot:
 + def __init__(self, engine):
 + def getList():
 + def load(self, name, rev = -1):
 + def save(self):
 + def clone(self):
 + def deserialize(self, data):
 + def serialize(self, data):
 + def isValid(self):
 + def random_id(length):
 + def generateToken():
 + def getNodeName():
 + def generateMgennId():
# class MgennConsts:
# class ApiTag:
# class ApiValus:
# class ApiRespState:
# class ApiCmd:
# class ApiAdminCmd:
# class BlState:
# class ListFilter:
# class ListFilterMod:
# class SnapshotState:
# class ApiAdminHelper:
 + def __init__(self, engine):
 + def getSnapshotNames(self):
