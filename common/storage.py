import psycopg2
from psycopg2 import sql
import uuid
import time
import jsonpickle
import json
from .timeline import *
from .functional import F

class PG_Pool:
    def __init__(self, db_conf):
        host, user, password, dbname = db_conf
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # минимальное количество соединений
            20,  # максимальное количество соединений
            user=user,
            password=password,
            host=host,
            port=5432,
            database=dbname
        )
    def __del__(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None

    def __exit__(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None

    @staticmethod
    def db_conf_from_env():
        # return db_host, db_user, db_password, db_name
        env = F.get_env(['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'])
        db_host = env['DB_HOST']
        db_user = env['DB_USER']
        db_password = env['DB_PASSWORD']
        db_name = env['DB_NAME']
        return db_host, db_user, db_password, db_name
    def connected(self) -> bool:
        return bool(self.connection_pool) and self.connection_pool.check_connected()

    def get_conn(self):
        return self.connection_pool.getconn()

    def put_conn(self, conn):
        return self.connection_pool.putconn(conn)

class PGUtils():
    def table_exists(self, cur, table_name, schema_name='public'):
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s
            )
        """)
        cur.execute(query, (schema_name, table_name))
        exists = cur.fetchone()[0]
        return exists

class ObjectStorage():
    def __init__(self, pool:PGUtils):
        if not pool:
            raise ValueError("no pg pool")
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
        self.cur.execute("SELECT count(object) as co FROM public.data WHERE (id=%s)", (key,))
        row = self.cur.fetchone()
        d = float(time.monotonic() - st) * 1000.
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
                self.pool.putconn(conn)
                return False
        self.pool.putconn(conn)
        return True

    def make_db(self):
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE public.data (
                _row bigint NOT NULL,
                id character varying(256) NOT NULL,
                object jsonb NOT NULL
            );
            """)
        cur.execute("""
            CREATE UNIQUE INDEX CONCURRENTLY obj_id
                ON public.data USING btree
                (id)
                WITH (fillfactor=20, deduplicate_items=True)
                TABLESPACE pg_default;
            """)
        conn.commit()
        self.pool.putconn(conn)

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
        self.pool.putconn(conn)
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
        row = self.cur.fetchone()

        if not row:
            raise IndexError("%s not found" % key)
        j = row[0]
        conn.commit()
        self.pool.putconn(conn)
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


class MgennStorage():
    def __init__(self, pool:PGUtils) -> None:
        self.pool = pool
        self.blob_storage = None

    def is_connected(self):
        return bool(self.blob_storage) and self.blob_storage.connected() and self.__bl_cur

    def init(self):
        if self.blob_storage:
            del self.blob_storage
            self.blob_storage = None
        self.blob_storage = ObjectStorage(self.pool)
        F.pring("MgennStorage init ok")
        if not self.check_db():
            F.print("make mgenn db")
            self.make_db()


    def __req_tables(self) -> list:
        # (schema_name, table_name)
        return [("public", "sys")]

    def check_db(self):
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        for schema_name, table_name in self.__req_tables():
            if not self.pgutils.table_exists(cur, table_name, schema_name):
                self.pool.putconn(conn)
                return False
        self.pool.putconn(conn)
        return True

    def make_db(self):
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE public.sys
            (
                key character varying(128) NOT NULL,
                s_val text,
                j_val jsonb,
                PRIMARY KEY (key)
            );
            """)
        cur.execute("""
            CREATE TABLE public.analyze_ready
            (
                task_id bigserial NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                rank smallint NOT NULL,
                tick bigint NOT NULL,
                ctime timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                outputs jsonb,
                creator character varying(256),
                exec_telemetry jsonb,
                ex jsonb,
                PRIMARY KEY (task_id)
            )
            """)
        cur.execute("""WITH ( autovacuum_enabled = TRUE );""")
        cur.execute("""ALTER TABLE IF EXISTS public.analyze_ready ADD CONSTRAINT u_snapshot UNIQUE (snapshot_id);""")

        cur.execute("""CREATE INDEX snapshot_rank_i ON public.analyze_ready USING btree (rank) WITH (deduplicate_items=True);""")
        cur.execute("""CREATE INDEX snapshot_id_i ON public.analyze_ready USING btree (snapshot_id) WITH (deduplicate_items=True);""")

        conn.commit()
        self.pool.putconn(conn)