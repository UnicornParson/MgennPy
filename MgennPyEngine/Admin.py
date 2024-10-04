import MgennPyEngine.ApiDefs as defs
class ApiAdminHelper:
	def __init__(self, engine):
		self.engine = engine;

	def getSnapshotNames(self):
		resp = self.engine.query(defs.ApiAdminCmd.CMD_GET_SNAPSHOTS_LIST)
		if not self.engine.isResponseOk(resp):
			print("invalid responce")
			return False

		return resp.content[defs.ApiTag.TAG_LIST]
