#from ApiDefs import *
#from MgennTools import *

import json
import requests
import time
import base64
from MgennPyEngine.ApiClient import *
import MgennPyEngine.MgennTools as mtools
import MgennPyEngine.ApiDefs as defs

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

    def getAlias(self, name):
        content = {defs.ApiTag.TAG_NAME: name}
        resp = self.query(defs.ApiCmd.CMD_ALIAS_GET, 0, content)
        if not self.isResponseOk(resp):
            print("invalid responce")
            return False
        return resp.content[defs.ApiTag.TAG_ALIAS]