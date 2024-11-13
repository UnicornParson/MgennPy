import platform
import hashlib
import random
import string
import ctypes
import time

class F():
    __nextId = 0

    @staticmethod
    def uhash(data):
        return ctypes.c_size_t(hash(data)).value

    @staticmethod
    def random_id(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def generateToken():
        return F.random_id(16) + "." + str(time.monotonic())

    @staticmethod
    def getNodeName():
        strName = platform.machine() + platform.version() + str(platform.uname()) + platform.processor()
        m = hashlib.sha512()
        m.update(strName.encode('utf-8'))
        nameHash = m.hexdigest()
        return nameHash

    @staticmethod
    def generateOID() -> int:
        id = F.__nextId
        F.__nextId += 1
        return id

    @staticmethod
    def generateMgennId() -> str:
        return "L%s.%s.%s" % (F.getNodeName() ,str(time.monotonic()).replace(".", ""), str(F.generateOID()))