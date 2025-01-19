import psycopg2
import uuid
import time
import jsonpickle
import json
from tools.timeline import *

class ObjectStorage():
    def __init__(self, db_conf):
        self.db_conf = db_conf
        host, user, password, dbname = db_conf
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port="5432", application_name="PyObjectStorage")
        self.cur = self.conn.cursor()
        self.timeline = Timeline()

    def __is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True
    
    def load_all(self, ds_key, fail = False) -> list:
        if not ds_key:
            raise ValueError("no key")
        obj = self.get(ds_key)
        if not obj or not isinstance(obj, list):
            print("ds map:", obj)
            raise ValueError("invalid ds map")
        check = self.check_dataset(obj, fail)
        if not check:
            return []
        return [self.get(x) for x in obj]
        

    def check_dataset(self, ds:list, fail = False) -> bool:
        for key in ds:
            if not key:
                continue
            if key not in self:
                if fail:
                    raise KeyError("no key %s " % str(key))
                return False
        return True

    def __contains__(self, key):
        st = time.monotonic()
        if not self.cur or not self.conn:
            raise ValueError("no cursor")
        if not key:
            raise ValueError("no key")
        self.cur.execute("SELECT count(object) as co FROM public.data WHERE (id=%s)", (key,))
        row = self.cur.fetchone()
        d = float(time.monotonic() - st) * 1000.
        self.timeline.add("contains_ms", d)
        return row != None and row[0] > 0

    def emplace(self, obj, key=None) -> str:
        st = time.monotonic()
        if not self.cur or not self.conn:
            raise ValueError("no cursor")
        if not obj:
            raise ValueError("no object")
        if not key:
            key = f"{uuid.uuid4().hex}.{time.time()}"
        j = jsonpickle.encode(obj)
        self.cur.execute("""
        INSERT INTO data (id, object)
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE
          SET id = %s, object = %s;
        """, (key, j, key, j))
        self.conn.commit()
        d = float(time.monotonic() - st) * 1000.
        self.timeline.add("emplace_ms", d)
        return key

    def get_many(self, keys) -> list:
        if not isinstance(keys, list):
            raise ValueError("keys not a list")
        l = []
        for k in keys:
            k_s = str(k)
            print("get obj for ", k_s)
            l.append(self.get(k_s))
        return l

    def get(self, key):
        st = time.monotonic()
        if not self.cur or not self.conn:
            raise ValueError("no cursor")
        if not key:
            raise ValueError("no key")
        self.cur.execute("SELECT object FROM public.data WHERE (id=%s)", (key,))
        row = self.cur.fetchone()
        if not row:
            raise IndexError("%s not found" % key)
        j = row[0]
        js = j
        if isinstance(js, dict) or isinstance(js, list):
            js = json.dumps(j)
        try:
            obj = jsonpickle.decode(js)
        except TypeError:
            print(js)
        d = float(time.monotonic() - st) * 1000.
        self.timeline.add("get_ms", d)
        return obj

    def perf_report(self):
        if "emplace_ms" in self.timeline:
            self.timeline.plot("emplace_ms")
        if "get_ms" in self.timeline:
            self.timeline.plot("get_ms")
        if "contains_ms" in self.timeline:
            self.timeline.plot("contains_ms")

    def __del__(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None
    def __exit__(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None