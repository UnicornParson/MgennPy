import sys
import json
import MgennPyEngine as mg
class cmdExecutor:
	def __init__(self, cfg):
		self.cmdList = ["help", "show" ,"create", "check", "list"]
		self.cfg = cfg
		try:
			url = cfg["apiurl"]
		except:
			print("invalid config file. missing data")
			exit(1)

		self.engine = mg.Engine(url)
		rc = self.engine.start()
		if not rc:
			print("cannot start engine")
			exit()
		self.admin = mg.ApiAdminHelper(self.engine)

	def isValisCommand(self, cmd):
		isValid = False
		for item in self.cmdList:
			if item == cmd:
				isValid = True
		return isValid

	def execCmd(self, cmd, args):
		print("exec %s(%s)" % (cmd, str(args)))
		cmd = cmd.lower()
		if cmd == "" or cmd == "help":
			self.printHelp()
			exit(0)
		if False == self.isValisCommand(cmd):
			print("command %s is not supported" % cmd)
			self.printHelp()
			exit(1)

		if cmd == "show":
			self.onShow(args)
		elif cmd == "create":
			self.onCreate(args)
		elif cmd == "check":
			self.onCheck(args)	
		elif cmd == "list":
			self.onList(args)	


	def printHelp(self):
		print("available commands:")
		for cmd in self.cmdList:
			print("  " + cmd)

	def onShow(self, args):
		if len(args) < 1:
			print("command Show: missing arguments")
			return


	def onList(self, args):
		if len(args) < 1:
			print("command List: missing arguments")
			return
		target = args[0].lower()
		if target == "snapshot" or target == "snp":
			list = self.admin.getSnapshotNames()
			for name in list:
				print(name + " => " + self.engine.getAlias(name))
		else:
			print("command List: unknown argument " + str(args))
			return




###############################################################################

print("MGENN console")
cfgFileName = "mgenn.cfg"
print("loading configs from " + cfgFileName )

cfg = 0
try:
	with open(cfgFileName) as json_data:
		cfg = json.load(json_data)
		print("done")
except:
	print("invalid configs. please check " + cfgFileName)
	exit(2)

cmd = "help"
args = []
if len(sys.argv) > 1:
	cmd = sys.argv[1]
	for i in range(2, (len(sys.argv))):
		args.append(sys.argv[i])

executor = cmdExecutor(cfg)
executor.execCmd(cmd, args)