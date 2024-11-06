import json
import api_defs as defs
import MgennTools as mtools
import requests
import time
import base64


class ApiRequest:
	def __init__(self, cmd = "", args = 0, content = 0):
		self.cmd = cmd
		self.args = args
		self.content = content
		self.token = mtools.generateToken()

class ApiResponceMeta:
	def __init__(self):
		self.state = defs.ApiRespState.RESP_STATE_UNKNOWN
		self.token = 0
		self.comment = 0
		self.originator = 0
		self.duration = 0
	def load(self, respMataObject):
		ret = False
		self.state = respMataObject[defs.ApiTag.TAG_STATE]
		self.token = respMataObject[defs.ApiTag.TAG_TOKEN]
		self.comment = respMataObject[defs.ApiTag.TAG_COMMENT]
		self.originator = respMataObject[defs.ApiTag.TAG_ORIGINATOR]
		ret = True
		return ret

class ApiResponce:
	def __init__(self):
		self.meta = ApiResponceMeta()
		self.content = 0
		self.state = 0
		self.token = mtools.generateToken()

	def load(self, respObject):
		ret = False
		try:
			metaObj = respObject[defs.ApiTag.TAG_META]
			self.meta.load(metaObj)
			self.content = respObject[defs.ApiTag.TAG_CONTENT]
			ret = True
		except AttributeError:
			print("invalid responce " + str(respObject))
		except KeyError:
			print("missing key in " + str(respObject))

		return ret

class ApiClient:
	def __init__(self, apiUrl):
		self.url = apiUrl

	def encondeContent(self, content):
		jsonText = json.dumps(content).encode("utf-8")
		b64 = base64.b64encode(jsonText)
		return b64.decode('ASCII')

	def query(self, request):
		startTime = time.time()
		ret = ApiResponce()
		reqUrl = "%s?%s=%s&%s=%s&%s=%s" % (self.url, defs.ApiTag.TAG_CMD, request.cmd, defs.ApiTag.TAG_ARGS, request.args, defs.ApiTag.TAG_TOKEN, request.token)
		payload = 0
		if request.content:
			payload = "content=" + self.encondeContent(request.content)

		headers = {
			"User-Agent": MgennConsts.User_Agent,
			"X-Custom-User-Agent": MgennConsts.User_Agent,
			"Content-Type": "application/x-www-form-urlencoded"
		}

		resp = requests.post(reqUrl, data = payload, headers=headers, allow_redirects = True, verify=False)
		try:
			respJson = resp.json()
		except:
			print("invalid responce foramt: " + resp.text)
			ret = ApiResponce()
			ret.meta.state = defs.ApiRespState.RESP_STATE_INVALID_RESPONCE
			return ret

		loadRc = ret.load(respJson)
		if loadRc == False:
			print("cannot parce responce " + str(respJson))
			ret = ApiResponce()
			ret.meta.state = defs.ApiRespState.RESP_STATE_INVALID_RESPONCE
			return ret

		doneTime = time.time()
		ret.meta.duration = doneTime - startTime
		return ret

		#connection.request('POST', '/', headers = headers)




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


class Engine:
	def __init__(self, apiUrl):
		self.url = apiUrl
		self.client = 0

	def start(self):
		if self.url == "":
			print("Empty ApiUrl")
			return False
		self.client = ApiClient(self.url)
		return True

	def query(self, cmd = "", args = 0, content = 0):
		if self.client == 0:
			print("engine is not started")
			return False
		req = ApiRequest(cmd, args, content)
		resp = self.client.query(req)
		return resp

	def isResponseOk(self, resp):
		return (resp.meta.state == defs.ApiRespState.RESP_STATE_OK)

	def getSnapshotList(self, filter = ""):
		args = 0
		if filter != "":
			args = filter

		resp = self.query(defs.ApiCmd.CMD_GET_SNAPSHOTS_LIST, args)

		if not self.isResponseOk(resp):
			print("invalid responce")
			return False

		return resp.content

class ApiAdminHelper:
	def __init__(self, engine):
		self.engine = engine

	def getSnapshotNames(self):
		resp = self.engine.query(defs.ApiAdminCmd.CMD_GET_SNAPSHOTS_LIST)
		if not self.engine.isResponseOk(resp):
			print("invalid responce")
			return False

		return resp.content[defs.ApiTag.TAG_LIST]


