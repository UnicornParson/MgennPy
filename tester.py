import MgennPyEngine as mg
import json

apiUrl = "http://192.168.44.214/mgenn/api.php"

engine = mg.Engine(apiUrl)
rc = engine.start()
if not rc:
	print("cannot start engine")
	exit()
admin = mg.ApiAdminHelper(engine)
list = admin.getSnapshotNames()

if not list:
	print("cannot get list")
	exit()

for name in list:
	print(name + " => " + engine.getAlias(name))

#snapshot = mg.Snapshot(engine)
#snapshot.load("ad")

#print("returned " + resp.meta.state + " with duration " + str(resp.meta.duration))
