import platform
import hashlib
import random
import string
import ctypes
import time
import datetime
import sys
import inspect
import os
import pandas as pd

class F():
    __nextId = 0
    __debug_env = "MGENN_DEBUG"

    @staticmethod
    def caller_str():
        cf = inspect.stack()[2]
        return f"[{cf.function}.{cf.lineno}]"

    @staticmethod
    def here_str():
        cf = inspect.stack()[1]
        return f"[{cf.function}.{cf.lineno}]"

    @staticmethod
    def print(*args, **kwargs):
        if F.__debug_env not in os.environ:
            return
        e_debug = os.environ[F.__debug_env]
        if e_debug != 1 and e_debug != "Y":
            return
        cf = inspect.stack()[1]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stdout.write(f"[{current_time}]in[{cf.function}.{cf.lineno}] ")
        return print(*args, **kwargs, flush=True)

    @staticmethod
    def uhash(data):
        ## hash(str(data)) hack for types like list of tuples or tuples of lists
        return ctypes.c_size_t(hash(str(data))).value

    @staticmethod
    def random_id(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def generateToken():
        token = F.random_id(16) + "." + str(time.monotonic())
        F.print(f"new token {token}")
        return token

    @staticmethod
    def dsort(x:dict) -> dict:
        if not isinstance(x, dict):
            raise ValueError(f"dsort only for dicts, {type(x)} received")
        return dict(sorted(x.items(), key=lambda item: item[0]))

    @staticmethod
    def d_eq(a:dict, b:dict, maybe_none=False):
        if a == None and b == None and maybe_none:
            F.print(f"p0 a:{a} b:{b}")
            return True
        if a == None or b == None:
            if not maybe_none:
                raise ValueError("None value")
            F.print("p1 a:{a} b:{b}")
            return False
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError("function works only with dicts!")
        if len(a) != len(b):
            F.print(f"p2 a:{a} b:{b}")
            return False
        for ak, av in a.items():
            try:
                bv = b[ak]
            except Exception:
                F.print(f"cannot extract {ak} from b")
                return False
            if type(av) != type(bv):
                F.print(f"p3 a:{a} b:{b}")
                return False
            if ak not in b:
                F.print(f"p4 a:{a} b:{b}")
                return False
            if isinstance(av, dict) and not F.d_eq(av, bv):
                F.print(f"p5 a:{a} b:{b}")
                return False
            if av != bv:
                F.print(f"p6 a:{a} b:{b}")
                return False
        F.print(f"p7 a:{a} b:{b}")
        return True

    @staticmethod
    def dsort_val(x:dict) -> dict:
        if not isinstance(x, dict):
            raise ValueError(f"dsort_val only for dicts, {type(x)} received")
        return dict(sorted(x.items(), key=lambda item: item[1]))

    @staticmethod
    def getNodeName():
        strName = platform.machine() + platform.version() + str(platform.uname()) + platform.processor()
        m = hashlib.sha512()
        m.update(strName.encode('utf-8'))
        nameHash = m.hexdigest()
        F.print(f"new node name {nameHash}")
        return nameHash

    @staticmethod
    def generateOID() -> int:
        id = F.__nextId
        F.__nextId += 1
        return id

    @staticmethod
    def generateMgennId() -> str:
        id = "L%s.%s.%s" % (F.getNodeName() ,str(time.monotonic()).replace(".", ""), str(F.generateOID()))
        F.print(f"new id {id}")
        return id

    @staticmethod
    def df2str(df:pd.DataFrame)->str:
        return ' | '.join(df.apply(lambda x: ':'.join(x.astype(str)), axis=1))