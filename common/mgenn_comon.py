import hashlib
import time
import os
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

        elif isinstance(obj, (float, np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int64, np.integer)):
            return int(obj)
        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return json.JSONEncoder.default(self, obj)

class TickTracer:
    __messages = []
    __tick = 0
    __coreid = ""
    output_file = f"./trace/{float(time.time())}_pid{os.getpid()}.txt"
    tracer_enabler = "TICKTRACE"

    @staticmethod
    def enabled() -> bool:
        if TickTracer.tracer_enabler not in os.environ:
            return False
        e_debug = os.environ[TickTracer.tracer_enabler]
        return e_debug == 1 or e_debug == "Y"

    @staticmethod
    def dump_to_file():
        if not TickTracer.enabled():
            return
        with open (TickTracer.output_file, "a") as file:
            file.write(f"------ dump start ------\n")
            msg = "\n".join(TickTracer.dump()) + "\n"
            file.write(msg)
            file.write(f"------ dump end ------\n\n")

    @staticmethod
    def start(tick, core_id) -> None:
        if not TickTracer.enabled():
            return
        TickTracer.__messages = []
        TickTracer.__tick = tick
        TickTracer.__coreid = core_id
    
    @staticmethod
    def dump() -> list:
        return TickTracer.__messages

    @staticmethod
    def trace(msg:str):
        if not TickTracer.enabled():
            return
        fmsg = f"{time.time()} - {TickTracer.__coreid}[{TickTracer.__tick}] {msg}"
        TickTracer.__messages.append (fmsg)

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
    
    @staticmethod
    def contains(val, arr) -> bool:
        # operator in does not work with numpy arrays and multilevel lists
        for item in arr:
            if isinstance(item, (list, np.ndarray)) and MgennComon.contains(val, item):
                return True
            if item == val:
                return True
        return False
    
    @staticmethod
    def grep_dict(data, target_key, current_path=""):
        """
        Recursively searches for a key in nested dictionaries/lists/tuples.
        Returns dict of {full_path: value} for all occurrences.
        
        :param data: Current data structure being searched
        :param target_key: Key to search for
        :param current_path: Dot-separated path of current location (for recursion)
        :return: Dictionary of {full_path: value} pairs
        """
        results = {}
        
        if isinstance(data, dict):
            # Check if current dict contains target key
            if target_key in data:
                full_path = f"{current_path}.{target_key}" if current_path else target_key
                results[full_path] = data[target_key]
            
            # Recurse through all key-value pairs
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                results.update(MgennComon.grep_dict(value, target_key, new_path))
        
        elif isinstance(data, (list, tuple)):
            # Recurse through list elements with index notation
            for idx, item in enumerate(data):
                new_path = f"{current_path}.{idx}"
                results.update(MgennComon.grep_dict(item, target_key, new_path))
        
        return results