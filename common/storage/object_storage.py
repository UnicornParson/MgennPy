import psycopg2
from psycopg2 import sql
import uuid
import time
import jsonpickle
import json
import pandas as pd
from ..timeline import *
from ..functional import F
from ..package import *
from ..functional import F

from .utils import *
from .pgpool import *

class ObjectStorage():
    def __init__(self, pool:PG_Pool):
        if not pool:
            raise ValueError("no pg pool")
        if not isinstance(pool, PG_Pool):
            raise ValueError(f"pg pool is not a pool {type(pool)}")

        ## check data on each action
        self.pedantic_validation = False

        self.pool = pool
        self.timeline = Timeline()
        self.pgutils = PGUtils()

        if not self.check_db():
            self.make_db()

    def connected(self) -> bool:
        return bool(self.pool) and self.pool.connected()

    def __req_tables(self) -> list:
        # (schema_name, table_name)
        return [("public", "data")]

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
        if not self.connected():
            raise Exception("not connected")
        if not key:
            raise ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT count(object) as co FROM public.data WHERE (id=%s)", (key,))
        row = cur.fetchone()
        d = float(time.monotonic() - st) * 1000.
        self.pool.put_conn(conn)
        self.timeline.add("contains_ms", d)
        return row != None and row[0] > 0

    def check_db(self) -> bool:
        if not self.connected():
            raise Exception("not connected")
            # def table_exists(self, cur, table_name, schema_name='public'):
        conn = self.pool.get_conn()
        cur = conn.cursor()
        for schema_name, table_name in self.__req_tables():
            if not self.pgutils.table_exists(cur, table_name, schema_name):
                self.pool.put_conn(conn)
                return False
        self.pool.put_conn(conn)
        return True

    def make_db(self):
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = True
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.data (
                _row bigserial NOT NULL,
                id character varying(256) NOT NULL,
                object jsonb NOT NULL
            );
            """)
        cur.execute("""
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS  obj_id
                ON public.data USING btree
                (id)
                WITH (fillfactor=20, deduplicate_items=True)
                TABLESPACE pg_default;
            """)
        conn.autocommit = False
        self.pool.put_conn(conn)

        if not self.check_db():
            raise Exception("invald db after install")

    def emplace(self, obj, key=None) -> str:
        st = time.monotonic()
        if not obj:
            raise ValueError("no object")
        if not key:
            key = f"{uuid.uuid4().hex}.{time.time()}"
        j = jsonpickle.encode(obj)
        conn = self.pool.get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO data (id, object)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE
            SET id = %s, object = %s;
        """, (key, j, key, j))
        conn.commit()
        self.pool.put_conn(conn)
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
        if not key:
            raise ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT object FROM public.data WHERE (id=%s)", (key,))
        row = cur.fetchone()

        if not row:
            raise IndexError("%s not found" % key)
        j = row[0]
        
        self.pool.put_conn(conn)
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

    ## erase with external db cursor. for run in already processed transactions
    def erase_excur(self, key:str, cur):
        if not key or not isinstance(key, str):
            return ValueError("no key")
        cur.execute(sql.SQL("DELETE FROM public.data WHERE (id=%s)"), (key,))

    def erase(self, key:str):
        if not key or not isinstance(key, str):
            return ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = True
        self.erase_excur(key, cur)
        self.pool.put_conn(conn)

