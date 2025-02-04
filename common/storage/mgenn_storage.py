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

# storage imports
from .errors import *
from .pgpool import *
from .utils import *
from .object_storage import *
from .job import *

class MgennStorage():
    def __init__(self, pool:PG_Pool) -> None:
        if not pool:
            raise ValueError("no pg pool")
        if not isinstance(pool, PG_Pool):
            raise ValueError(f"pg pool is not a pool {type(pool)}")
        if not pool.connected():
            raise ValueError("pool is not connected")

        self.pool = pool
        self.pgutils = PGUtils()
        self.blob_storage = None

    def connected(self):
        return bool(self.blob_storage) and self.blob_storage.connected() and bool(self.pool) and self.pool.connected()

    def init(self):
        if self.blob_storage:
            del self.blob_storage
            self.blob_storage = None
        self.blob_storage = ObjectStorage(self.pool)
        F.print("MgennStorage init ok")
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
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS public.sys
            (
                key character varying(128) NOT NULL,
                s_val text,
                j_val jsonb,
                PRIMARY KEY (key)
            );
            """))
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS public.analyze_ready
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
            ) WITH ( autovacuum_enabled = TRUE )
            """))
        cur.execute(sql.SQL("""ALTER TABLE IF EXISTS public.analyze_ready ADD CONSTRAINT u_snapshot UNIQUE (snapshot_id);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_rank_i ON public.analyze_ready USING btree (rank) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_id_i ON public.analyze_ready USING btree (snapshot_id) WITH (deduplicate_items=True);"""))

        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS public.busy_by_analizer
            (
                task_id bigint NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                rank smallint NOT NULL,
                tick bigint NOT NULL,
                ctime timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                outputs jsonb,
                creator character varying(256),
                owner character varying(256),
                exec_telemetry jsonb,
                ex jsonb,
                PRIMARY KEY (task_id)
            ) WITH ( autovacuum_enabled = TRUE )
            """))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_id_i ON public.busy_by_analizer USING btree (snapshot_id) WITH (deduplicate_items=True);"""))

        conn.autocommit = False
        self.pool.put_conn(conn)

    def checkout_analizer_job(self, snapshot_id):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            raise ValueError("no snapshot id")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        last_e = None
        try:
            cur.execute(sql.SQL("""
            INSERT INTO public.busy_by_analizer ( 
                    task_id,
                    snapshot_id,
                    rank,
                    tick,
                    ctime,
                    outputs,
                    creator,
                    exec_telemetry,
                    ex
            )
            SELECT 
                public.analyze_ready.task_id,
                public.analyze_ready.snapshot_id,
                public.analyze_ready.rank,
                public.analyze_ready.tick,
                public.analyze_ready.ctime,
                public.analyze_ready.outputs,
                public.analyze_ready.creator,
                public.analyze_ready.exec_telemetry,
                public.analyze_ready.ex
            FROM    public.analyze_ready
            WHERE   public.analyze_ready.snapshot_id = %s
            LIMIT 0, 1;"""), (snapshot_id,))
            if cur.rowcount != 1:
                raise psycopg2.IntegrityError(f"invalid task checkout. affected:{cur.rowcount} id:{snapshot_id}")
            job =  AnalizerJob.from_db("public.busy_by_analizer", snapshot_id, cur)

            if not job:
                raise psycopg2.IntegrityError(f"no marked for checkout job with id {snapshot_id}")

            cur.execute(sql.SQL("DELETE FROM analyze_ready WHERE public.analyze_ready.snapshot_id = %s"), (snapshot_id,))
            conn.commit()
        except Exception as e:
            F.print(f"checkout failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e


        ## FIXME return pkg and co data
    def undo_analyzer_checkout(self, snapshot_id):
        pass


    def on_exec_done(self, pkg:Package, rank:int, outputs:pd.DataFrame, telemetry = {}, ex = {}):
        if not self.connected():
            raise Exception("not connected")
        if not pkg or not pkg.isValid():
            raise ValueError("invalid package")
        j_out = jsonpickle.encode(outputs.to_dict('list'))
        tick = int(pkg.tick)
        sid = pkg.id()
        app_name = F.getNodeFullName()

        if sid in self.blob_storage:
            raise Exception(f"package [{sid}]already stored")
        _, jpkg = pkg.dump()
        sid = self.blob_storage.emplace(jpkg, sid)
        if sid not in self.blob_storage:
            raise Exception("object [{sid}] not saved")
        q = sql.SQL("""
            INSERT INTO public.analyze_ready(
                snapshot_id, rank, tick, ctime, outputs, creator, exec_telemetry, ex) 
            VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s);
        """)
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        last_e = None
        try:
            cur.execute(q, (sid, rank, tick, F.jsump(j_out), app_name, F.jsump(telemetry), F.jsump(ex)))
            conn.commit()
        except Exception as e:
            F.print(f"save pkg failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e

    def erase_snapshot(self, snapshot_id):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            return ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        last_e = None
        try:
            # remove all records
            cur.execute(sql.SQL("DELETE FROM public.analyze_ready WHERE (snapshot_id=%s)"), (snapshot_id,))
            cur.execute(sql.SQL("DELETE FROM public.busy_by_analizer WHERE (snapshot_id=%s)"), (snapshot_id,))
            # remove object
            self.blob_storage.erase_excur(snapshot_id, cur)
            conn.commit()
        except Exception as e:
            F.print(f"erase [{snapshot_id}] failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e