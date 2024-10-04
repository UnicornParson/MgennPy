
import json
import requests
import time
import base64

import MgennPyEngine.MgennTools as mtools
import MgennPyEngine.ApiDefs as defs

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
		self.state = respMataObject[defs.ApiTag.TAG_STATE];
		self.token = respMataObject[defs.ApiTag.TAG_TOKEN];
		self.comment = respMataObject[defs.ApiTag.TAG_COMMENT];
		self.originator = respMataObject[defs.ApiTag.TAG_ORIGINATOR];
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
		self.url = apiUrl;

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
			"User-Agent": defs.MgennConsts.User_Agent,
			"X-Custom-User-Agent": defs.MgennConsts.User_Agent,
			"Content-Type": "application/x-www-form-urlencoded"
		}

		resp = requests.post(reqUrl, data = payload, headers=headers, allow_redirects = True, verify=False)
		try:
			respJson = resp.json()
		except:
			print("invalid responce foramt: " + resp.text)
			ret = ApiResponce()
			ret.meta.state = defs.ApiRespState.RESP_STATE_INVALID_RESPONCE
			return ret;

		loadRc = ret.load(respJson)
		if loadRc == False:
			print("cannot parce responce " + str(respJson))
			ret = ApiResponce()
			ret.meta.state = defs.ApiRespState.RESP_STATE_INVALID_RESPONCE
			return ret;

		doneTime = time.time()
		ret.meta.duration = doneTime - startTime
		return ret
