import random, string, time
import platform
import hashlib
__nextId = 0
def random_id(length):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(length))

def generateToken():
  return random_id(16) + "." + str(time.monotonic())

def getNodeName():
	strName = platform.machine() + platform.version() + str(platform.uname()) + platform.processor()
	m = hashlib.sha512()
	m.update(strName.encode('utf-8'))
	nameHash = m.hexdigest()
	return nameHash

def generateMgennId():
	global __nextId
	id = __nextId
	__nextId += 1
	return "L%s.%s.%s" % (getNodeName() ,str(time.monotonic()).replace(".", ""), str(id))