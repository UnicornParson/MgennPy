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
        """
        Returns the string representation of the current function call.

        :return: str
        """
        cf = inspect.stack()[2]
        return f"[{cf.function}.{cf.lineno}]"

    @staticmethod
    def here_str():
        """
        Returns the string representation of the current frame.

        :return: str
        """
        cf = inspect.stack()[1]
        return f"[{cf.function}.{cf.lineno}]"

    @staticmethod
    def make_quiet():
        """
        Disable debug print
        """
        os.environ[F.__debug_env] = "N"

    @staticmethod
    def make_verbose():
        """
        Enable debug print
        """
        os.environ[F.__debug_env] = "Y"

    @staticmethod
    def print(*args, **kwargs):
        """
        Prints a message with the current timestamp and function name.

        :param args: Any arguments to be printed.
        :param kwargs: Any keyword arguments to be printed.
        """
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
    def uhash(data) -> int:
        """
        Hashes the input data using a custom implementation.

        :param data: The input data to be hashed.
        :return: An integer hash value.
        """
        ## hash(str(data)) hack for types like list of tuples or tuples of lists
        return ctypes.c_size_t(hash(str(data))).value

    @staticmethod
    def random_id(length):
        """
        Generates a random ID string of the specified length.

        :param length: The desired length of the ID string.
        :return: A random ID string.
        """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def generateToken():
        """
        Generates a new token with the current timestamp.

        :return: A new token with the current timestamp.
        """
        token = F.random_id(16) + "." + str(time.monotonic())
        F.print(f"new token {token}")
        return token

    @staticmethod
    def dsort(x:dict) -> dict:
        """
        Sorts a dictionary by its keys.

        :param x: The input dictionary to be sorted.
        :return: A new dictionary with the same values but in sorted order by key.
        """
        if not isinstance(x, dict):
            raise ValueError(f"dsort only for dicts, {type(x)} received")
        return dict(sorted(x.items(), key=lambda item: item[0]))

    @staticmethod
    def l_eq(list1, list2, maybe_none=False):
        """
        Compares two lists for equality.

        :param list1: The first list to compare.
        :param list2: The second list to compare.
        :param maybe_none: If both lists are None, returns True.
        :return: A boolean indicating whether the lists are equal.
        """
        if list1 == None and list2 == None and maybe_none:
            F.print(f"p0 a:{list1} b:{list2}")
            return True
        if len(list1) != len(list2):
            return False
        for obj1, obj2 in zip(list1, list2):
            if obj1 != obj2 :
                return False
        return True

    @staticmethod
    def d_eq(a:dict, b:dict, maybe_none=False, explain=False):
        """
        Compares two dictionaries for equality.

        :param a: The first dictionary to compare.
        :param b: The second dictionary to compare.
        :param maybe_none: If both dictionaries are None, returns True.
        :param explain: If enabled, prints explanations for non-equal values.
        :return: A boolean indicating whether the dictionaries are equal.
        """
        if a == None and b == None and maybe_none:
            return True
        if a == None or b == None:
            if not maybe_none:
                raise ValueError("None value")
            if explain:
                F.print("p1 None value a:{a} b:{b}")
            return False
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError("function works only with dicts!")
        if len(a) != len(b):
            if explain:
                F.print(f"different len  a({len(a)}):{a} b({len(b)}):{b}")
            return False
        for ak, av in a.items():
            try:
                bv = b[ak]
            except Exception:
                if explain:
                    F.print(f"cannot extract {ak} from b")
                return False
            if type(av) != type(bv):
                if explain:
                    F.print(f"different types a:{av} b:{bv}")
                return False
            if ak not in b:
                if explain:
                    F.print(f"a:{a}::{ak} not in b:{b}")
                return False
            if isinstance(av, dict) and not F.d_eq(av, bv):
                if explain:
                    F.print(f"dict and not dict a:{a} b:{b}")
                return False
            if av != bv:
                if explain:
                    F.print(f"{av} != {bv} in a:{a} b:{b}")
                return False
        if explain:
            F.print(f"same dicts a:{a} b:{b}")
        return True

    @staticmethod
    def dsort_val(x:dict) -> dict:
        """
        Sorts a dictionary by its values.

        :param x: The input dictionary to be sorted.
        :return: A new dictionary with the same keys but in sorted order by value.
        """
        if not isinstance(x, dict):
            raise ValueError(f"dsort_val only for dicts, {type(x)} received")
        return dict(sorted(x.items(), key=lambda item: item[1]))

    @staticmethod
    def getNodeName():
        """
        Returns a unique identifier for the current node.

        :return: A string representing the node's name.
        """
        strName = platform.machine() + platform.version() + str(platform.uname()) + platform.processor()
        m = hashlib.sha512()
        m.update(strName.encode('utf-8'))
        nameHash = m.hexdigest()
        F.print(f"new node name {nameHash}")
        return nameHash

    @staticmethod
    def generateOID() -> int:
        """
        Generates a new unique ID.

        :return: An integer representing the new ID.
        """
        id = F.__nextId
        F.__nextId += 1
        return id

    @staticmethod
    def generateMgennId() -> str:
        """
        Generates a unique identifier for MGenn.

        :return: A string representing the new ID.
        """
        id = "L%s.%s.%s" % (F.getNodeName() ,str(time.monotonic()).replace(".", ""), str(F.generateOID()))
        F.print(f"new id {id}")
        return id

    @staticmethod
    def df2str(df:pd.DataFrame)->str:
        """
        Converts a pandas DataFrame to a string representation.

        :param df: The input DataFrame.
        :return: A string representation of the DataFrame.
        """
        return ' | '.join(df.apply(lambda x: ':'.join(x.astype(str)), axis=1))