import hashlib
import time
import platform
import numpy as np
import json
from .mgenn_consts import MgennConsts

class NumpyEncoder(json.JSONEncoder):
	""" Custom encoder for numpy data types """
	def default(self, obj):
		if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
							np.int16, np.int32, np.int64, np.uint8,
							np.uint16, np.uint32, np.uint64)):

			return str(obj)

		elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
			return float(obj)

		elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
			return {'real': obj.real, 'imag': obj.imag}

		elif isinstance(obj, (np.ndarray,)):
			return obj.tolist()

		elif isinstance(obj, (np.bool_)):
			return bool(obj)

		elif isinstance(obj, (np.void)):
			return None

		return json.JSONEncoder.default(self, obj)

class MgennComon:
	nextid = 0
	@staticmethod
	def getNodeName():
		strName = platform.machine() + platform.version() + str(platform.uname()) + platform.processor()
		m = hashlib.sha256()
		m.update(strName.encode('utf-8'))
		nameHash = m.hexdigest()
		return nameHash

	@staticmethod
	def getLocalId():
		MgennComon.nextid = MgennComon.nextid + 1
		return np.int64(MgennComon.nextid)

	@staticmethod
	def makeId(objPrefix: str):
		MgennComon.nextid = MgennComon.nextid + 1
		return "L%s_%s_%s.%d.%d" % (objPrefix, "PYMGENN", MgennComon.getNodeName(), round(time.time() * 1000), MgennComon.nextid)

	@staticmethod
	def mround(num):
	   return round(num, MgennConsts.Calc_accuracy)

	@staticmethod
	def hasMissingKeys(dictionary: dict, keys: list) -> bool:
		return len(set(keys) - set(dictionary.keys())) > 0
