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
        self.db_conf = db_conf
        host, user, password, dbname = db_conf
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port="5432", application_name="PyObjectStorage")
        self.cur = self.conn.cursor()
        self.timeline = Timeline()
        self.pgutils = PGUtils()

        if not self.check_db():
            self.make_db()

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
        return bool(self.conn) and bool(self.cur)

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
        for schema_name, table_name in self.__req_tables():
            if not self.pgutils.table_exists(self.cur, table_name, schema_name):
                return False
        return True

    def make_db(self):
        if not self.connected():
            raise Exception("not connected")
        self.cur.execute("""
            CREATE TABLE public.data (
                _row bigint NOT NULL,
                id character varying(256) NOT NULL,
                object jsonb NOT NULL
            );
            """)
        self.cur.execute("""
            CREATE UNIQUE INDEX CONCURRENTLY obj_id
                ON public.data USING btree
                (id)
                WITH (fillfactor=20, deduplicate_items=True)
                TABLESPACE pg_default;
            """)
        self.conn.commit()

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


class MgennStorage():
    def __init__(self, db_conf) -> None:
        self.db_conf = db_conf
        self.blob_storage = None
        self.__bl_conn = None
        self.__bl_cur = None

    def __del__(self):
        if self.__bl_cur:
            self.__bl_cur.close()
            self.__bl_cur = None
        if self.__bl_conn:
            self.__bl_conn.close()
            self.__bl_conn = None

    def __exit__(self):
        if self.__bl_cur:
            self.__bl_cur.close()
            self.__bl_cur = None
        if self.__bl_conn:
            self.__bl_conn.close()
            self.__bl_conn = None

    def is_connected(self):
        return bool(self.blob_storage) and self.blob_storage.connected() and self.__bl_cur

    def init(self):
        if self.blob_storage:
            del self.blob_storage
            self.blob_storage = None
        self.blob_storage = ObjectStorage(self.db_conf)
        if self.__bl_cur:
            self.__bl_cur.close()
            self.__bl_cur = None
        if self.__bl_conn:
            self.__bl_conn.close()
            self.__bl_conn = None
        host, user, password, dbname = self.db_conf
        self.__bl_conn = psycopg2.connect(dbname=dbname, 
                                    user=user, 
                                    assword=password,
                                    host=host,
                                    port="5432", 
                                    application_name="PyMgennStorage")
        self.__bl_cur = self.conn.cursor()
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
        for schema_name, table_name in self.__req_tables():
            if not self.pgutils.table_exists(self.cur, table_name, schema_name):
                return False
        return True

    def make_db(self):
        if not self.connected():
            raise Exception("not connected")
        self.cur.execute("""
            CREATE TABLE public.sys
            (
                key character varying(128) NOT NULL,
                s_val text,
                j_val jsonb,
                PRIMARY KEY (key)
            );
            """)
        self.cur.execute("""
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
        self.cur.execute("""WITH ( autovacuum_enabled = TRUE );""")
        self.cur.execute("""ALTER TABLE IF EXISTS public.analyze_ready ADD CONSTRAINT u_snapshot UNIQUE (snapshot_id);""")

        self.cur.execute("""CREATE INDEX snapshot_rank_i ON public.analyze_ready USING btree (rank) WITH (deduplicate_items=True);""")
        self.cur.execute("""CREATE INDEX snapshot_id_i ON public.analyze_ready USING btree (snapshot_id) WITH (deduplicate_items=True);""")

        self.conn.commit()