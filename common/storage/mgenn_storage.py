import psycopg2
from psycopg2 import sql

import uuid
import time
import jsonpickle
import json
import pandas as pd
import random
from ..timeline import *
from ..functional import F, W
from ..package import *

# storage imports
from .errors import *
from .pgpool import *
from .utils import *
from .object_storage import *
from .job import *

"""
abbreviations:

 +  [PV] - pedantic_validation
 +  AB - busy_by_analizer table
 +  AR - analyze_ready table
 +  ER - exec_ready
 +  EB - exec_busy
"""

class MgennStorageStats:
    def __init__(self) -> None:
        self.analyze_ready_size = 0
        self.busy_by_analizer_size = 0
        self.exec_ready_size = 0
        self.busy_by_executor_size = 0
        # durations
        self.eb_max_duration = 0.0
        self.ab_max_duration = 0.0
        # errors
        self.error_ab_ar_collision = 0
        self.error_eb_er_collision = 0
        

    def __repr__(self):
        return (
            f"MgennStorageStats("
            f"AR_size:{self.analyze_ready_size}, "
            f"AB_size:{self.busy_by_analizer_size}, "
            f"ER_size:{self.exec_ready_size}, "
            f"EB_size:{self.busy_by_executor_size}, "
            f"AB_duration:{self.ab_max_duration:0.2f}, "
            f"EB_duration:{self.eb_max_duration:0.2f}, "
            f"AR/AB_collision={self.error_ab_ar_collision}, "
            f"ER/EB_collision={self.error_eb_er_collision}"
            ")"
        )
    @staticmethod
    def load(cur):
        """
        public.analyze_ready
        public.busy_by_analizer
        task_id
        """
        stat = MgennStorageStats()
        cur.execute(sql.SQL("""SELECT COUNT(public.analyze_ready.task_id) as ar_count FROM public.analyze_ready"""))
        row = cur.fetchone()
        stat.analyze_ready_size = int(row[0])
        cur.execute(sql.SQL("""SELECT COUNT(public.busy_by_analizer.task_id) as ab_count FROM public.busy_by_analizer"""))
        row = cur.fetchone()
        stat.busy_by_analizer_size = int(row[0])

        cur.execute(sql.SQL("""SELECT COUNT(public.exec_ready.task_id) as er_count FROM public.exec_ready"""))
        row = cur.fetchone()
        stat.exec_ready_size = int(row[0])
        cur.execute(sql.SQL("""SELECT COUNT(public.busy_by_executor.task_id) as er_count FROM public.busy_by_executor"""))
        row = cur.fetchone()
        stat.busy_by_executor_size = int(row[0])

        # durations
        cur.execute(sql.SQL("""SELECT MAX(s) as ms FROM public.\"AB_duration\""""))
        row = cur.fetchone()
        stat.ab_max_duration = 0.0
        if row and row[0]:
            stat.ab_max_duration = float(row[0])
        cur.execute(sql.SQL("""SELECT MAX(s) as ms FROM public.\"EB_duration\""""))
        row = cur.fetchone()
        stat.eb_max_duration = 0.0
        if row and row[0]:
            stat.eb_max_duration = float(row[0])

        # errors
        cur.execute(sql.SQL("""
            SELECT COUNT(*) as cnt FROM public.busy_by_analizer bba1 
            JOIN public.analyze_ready ar ON bba1.task_id = ar.task_id AND bba1.snapshot_id = ar.snapshot_id;
        """))
        row = cur.fetchone()
        stat.error_ab_ar_collision = int(row[0])
        cur.execute(sql.SQL("""
            SELECT COUNT(*) as cnt FROM public.busy_by_executor bba1 
            JOIN public.exec_ready ar ON bba1.task_id = ar.task_id AND bba1.snapshot_id = ar.snapshot_id;
        """))
        row = cur.fetchone()
        stat.error_eb_er_collision = int(row[0])
        return stat

class StorageTable(enum.Enum):
    Notable = "no_table"
    AB = "busy_by_analizer"
    AR = "analyze_ready"


class MgennStorage():
    NO_GROUP_DEFAULT = "NOGROUP"
    def __init__(self, pool:PG_Pool) -> None:
        if not pool:
            raise ValueError("no pg pool")
        if not isinstance(pool, PG_Pool):
            raise ValueError(f"pg pool is not a pool {type(pool)}")
        if not pool.connected():
            raise ValueError("pool is not connected")
        ## check data on each action
        self.pedantic_validation = False
        self.pool = pool
        self.pgutils = PGUtils()
        self.blob_storage = None

    def connected(self):
        return bool(self.blob_storage) and self.blob_storage.connected() and bool(self.pool) and self.pool.connected()

    def __sid_in_table(self, snapshot_id:str, table:str,  cur) -> bool:
        cur.execute(sql.SQL(f"SELECT snapshot_id FROM {table} WHERE (snapshot_id = %s) LIMIT 1;"), (snapshot_id,))
        return cur.rowcount >= 1

    def stats(self):
        conn = self.pool.get_conn()
        cur = conn.cursor()
        s = MgennStorageStats.load(cur)
        self.pool.put_conn(conn)
        return s
    def labels(self, cur = None):
        # TODO: implement
        pass

    def init(self):
        if self.blob_storage:
            del self.blob_storage
            self.blob_storage = None
        self.blob_storage = ObjectStorage(self.pool)
        self.blob_storage.pedantic_validation = self.pedantic_validation
        F.print("MgennStorage init ok")
        if not self.check_db():
            F.print("make mgenn db")
            self.make_db()

    def find_snapshot(self, snapshot_id:str) -> StorageTable:
        if not snapshot_id:
            raise ValueError("no sid")
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        ret = StorageTable.Notable
        if self.__sid_in_table(snapshot_id, "public.analyze_ready", cur):
            ret = StorageTable.AR
        elif self.__sid_in_table(snapshot_id, "public.busy_by_analizer", cur):
            ret = StorageTable.AB
        self.pool.put_conn(conn)

        return ret


    def __req_tables(self) -> list:
        # (schema_name, table_name)
        return [
            ("public", "sys"),
            ("public", "analyze_ready"),
            ("public", "busy_by_analizer"),
            ("public", "exec_ready"),
            ("public", "busy_by_executor"),
            ("public", "done"),
            ]

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
        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS public.analyze_ready
            (
                task_id bigserial NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                snapshot_group character varying(256) NOT NULL DEFAULT '{MgennStorage.NO_GROUP_DEFAULT}',
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
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_group_i ON public.analyze_ready USING btree (snapshot_group) WITH (deduplicate_items=True);"""))
        
        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS public.busy_by_analizer
            (
                task_id bigint NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                snapshot_group character varying(256) NOT NULL DEFAULT '{MgennStorage.NO_GROUP_DEFAULT}',
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
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_group_i ON public.busy_by_analizer USING btree (snapshot_group) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS rank_i ON public.busy_by_analizer USING btree (rank) WITH (deduplicate_items=True);"""))

        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS public.exec_ready
            (
                task_id bigserial NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                snapshot_group character varying(256) NOT NULL DEFAULT '{MgennStorage.NO_GROUP_DEFAULT}',
                rank smallint NOT NULL,
                tick bigint NOT NULL,
                ctime timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ex jsonb,
                PRIMARY KEY (task_id)
            ) WITH ( autovacuum_enabled = TRUE )
            """))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_id_i ON public.exec_ready USING btree (snapshot_id) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS rank_i ON public.exec_ready USING btree (rank) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_group_i ON public.exec_ready USING btree (snapshot_group) WITH (deduplicate_items=True);"""))

        
        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS public.busy_by_executor
            (
                task_id bigserial NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                snapshot_group character varying(256) NOT NULL DEFAULT '{MgennStorage.NO_GROUP_DEFAULT}',
                rank smallint NOT NULL,
                tick bigint NOT NULL,
                ctime timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ex jsonb,
                PRIMARY KEY (task_id)
            ) WITH ( autovacuum_enabled = TRUE )
            """))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_id_i ON public.busy_by_executor USING btree (snapshot_id) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS rank_i ON public.busy_by_executor USING btree (rank) WITH (deduplicate_items=True);"""))
        cur.execute(sql.SQL("""CREATE INDEX IF NOT EXISTS snapshot_group_i ON public.busy_by_executor USING btree (snapshot_group) WITH (deduplicate_items=True);"""))

        cur.execute(sql.SQL(f"""
            CREATE TABLE public.done
            (
                i bigserial NOT NULL,
                snapshot_id character varying(256) NOT NULL,
                snapshot_group character varying(256) NOT NULL DEFAULT '{MgennStorage.NO_GROUP_DEFAULT}',
                last_owner character varying(512),
                reason character varying(512),
                ex jsonb,
                PRIMARY KEY (i)
            );
            """))
            
        # views
        cur.execute(sql.SQL("""
            CREATE VIEW public."EB_duration" AS
                SELECT task_id as tid, snapshot_group as sg, snapshot_id as sid, (NOW()-ctime) as duration, EXTRACT(EPOCH FROM (NOW()-ctime)) as s
                FROM public.busy_by_executor 
                ORDER BY (NOW()-ctime) DESC;
            """))
        cur.execute(sql.SQL("""COMMENT ON VIEW public."EB_duration" IS 'executor busy durations';"""))
        cur.execute(sql.SQL("""
            CREATE VIEW public."AB_duration" AS
                SELECT task_id as tid, snapshot_id as sid, snapshot_group as sg, (NOW()-ctime) as duration, EXTRACT(EPOCH FROM (NOW()-ctime)) as s
                FROM public.busy_by_analizer 
                ORDER BY (NOW()-ctime) DESC;
            """))
        cur.execute(sql.SQL("""COMMENT ON VIEW public."AB_duration" IS 'executor busy durations';"""))

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
            if not self.__sid_in_table(snapshot_id, "public.analyze_ready", cur):
                raise StorageKeyNotFoundError(snapshot_id, "AR")
            cur.execute(sql.SQL("""
            INSERT INTO public.busy_by_analizer ( 
                    task_id,
                    snapshot_id,
                    snapshot_group,
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
                public.analyze_ready.snapshot_group,
                public.analyze_ready.rank,
                public.analyze_ready.tick,
                public.analyze_ready.ctime,
                public.analyze_ready.outputs,
                public.analyze_ready.creator,
                public.analyze_ready.exec_telemetry,
                public.analyze_ready.ex
            FROM    public.analyze_ready
            WHERE   public.analyze_ready.snapshot_id = %s
            LIMIT 1;"""), (snapshot_id,))
            if cur.rowcount != 1:
                raise StorageIntegrityError(f"invalid task AR checkout. affected:{cur.rowcount} id:{snapshot_id}")

            job =  AnalizerJob.from_db("public.busy_by_analizer", snapshot_id, cur)

            if not job or not job.isValid():
                raise StorageIntegrityError(f"no marked for checkout job with id {snapshot_id}")

            cur.execute(sql.SQL("DELETE FROM analyze_ready WHERE public.analyze_ready.snapshot_id = %s"), (snapshot_id,))
            if self.pedantic_validation:
                if self.__sid_in_table(snapshot_id, "public.analyze_ready", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be removed from AR")
                if not self.__sid_in_table(snapshot_id, "public.busy_by_analizer", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be added to AB")
            conn.commit()
        except Exception as e:
            F.print(f"checkout failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e
        pkg_data = self.blob_storage.get(job.snapshot_id)
        pkg = Package()
        pkg.loadData(pkg_data)
        return job, pkg

    def undo_analyzer_checkout(self, snapshot_id):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            raise ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        last_e = None
        try:
            if not self.__sid_in_table(snapshot_id, "public.busy_by_analizer", cur):
                raise StorageKeyNotFoundError(snapshot_id, "AB")
            # move back to ready list
            cur.execute(sql.SQL("""
            INSERT INTO public.analyze_ready ( 
                    task_id,
                    snapshot_id,
                    snapshot_group,
                    rank,
                    tick,
                    ctime,
                    outputs,
                    creator,
                    exec_telemetry,
                    ex
            )
            SELECT 
                public.busy_by_analizer.task_id,
                public.busy_by_analizer.snapshot_id,
                public.busy_by_analizer.snapshot_group,
                public.busy_by_analizer.rank,
                public.busy_by_analizer.tick,
                public.busy_by_analizer.ctime,
                public.busy_by_analizer.outputs,
                public.busy_by_analizer.creator,
                public.busy_by_analizer.exec_telemetry,
                public.busy_by_analizer.ex
            FROM    public.busy_by_analizer
            WHERE   public.busy_by_analizer.snapshot_id = %s
            LIMIT 1;"""), (snapshot_id,))
            if cur.rowcount != 1:
                raise StorageIntegrityError(f"invalid task AB checkout undo. affected:{cur.rowcount} id:{snapshot_id}")
            # cleanup busy list
            cur.execute(sql.SQL("DELETE FROM public.busy_by_analizer WHERE (snapshot_id=%s)"), (snapshot_id,))
            conn.commit()

            if self.pedantic_validation:
                if self.__sid_in_table(snapshot_id, "public.busy_by_analizer", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be removed from AB")
                if not self.__sid_in_table(snapshot_id, "public.analyze_ready", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be added to AR")

        except Exception as e:
            F.print(f"erase [{snapshot_id}] failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e


    def on_exec_done(self, pkg:Package, rank:int, outputs:pd.DataFrame, label=NO_GROUP_DEFAULT, telemetry = {}, ex = {}):
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
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False

        if self.__sid_in_table(sid, "public.analyze_ready", cur):
            raise Exception("object [{sid}] already in AR backlog")

        q = sql.SQL("""
            INSERT INTO public.analyze_ready(
                snapshot_id, snapshot_group, rank, tick, ctime, outputs, creator, exec_telemetry, ex) 
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s);
        """)

        last_e = None
        try:
            cur.execute(q, (sid, label, rank, tick, F.jsump(j_out), app_name, F.jsump(telemetry), F.jsump(ex)))
            conn.commit()
            if self.pedantic_validation and not self.__sid_in_table(sid, "public.analyze_ready", cur):
                raise Exception("[PV] object [{sid}] already in AR backlog")
        except Exception as e:
            F.print(f"on_exec_done failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e

    def erase_snapshot(self, snapshot_id):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            raise ValueError("no key")

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

    def checkout_executor_job(self, snapshot_id, cur = None):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            raise ValueError("no snapshot id")
        push_conn = False
        conn = None
        if not cur:
            conn = self.pool.get_conn()
            cur = conn.cursor()
            push_conn = True
        conn.autocommit = False
        last_e = None
        job = None
        try:
            if not self.__sid_in_table(snapshot_id, "public.exec_ready", cur):
                raise StorageKeyNotFoundError(snapshot_id, "ER")
            cur.execute(sql.SQL("""
            INSERT INTO public.busy_by_executor ( 
                    task_id,
                    snapshot_id,
                    snapshot_group,
                    rank,
                    tick,
                    ctime,
                    ex
            )
            SELECT 
                public.exec_ready.task_id,
                public.exec_ready.snapshot_id,
                public.exec_ready.snapshot_group,
                public.exec_ready.rank,
                public.exec_ready.tick,
                public.exec_ready.ctime,
                public.exec_ready.ex
            FROM    public.exec_ready
            WHERE   public.exec_ready.snapshot_id = %s
            LIMIT 1;"""), (snapshot_id,))
            if cur.rowcount != 1:
                raise StorageIntegrityError(f"invalid task ER checkout. affected:{cur.rowcount} id:{snapshot_id}")

            job =  ExecutorJob.from_db("public.busy_by_executor", snapshot_id, cur)

            if not job or not job.isValid():
                raise StorageIntegrityError(f"no marked for checkout job with id {snapshot_id}")

            cur.execute(sql.SQL("DELETE FROM exec_ready WHERE public.exec_ready.snapshot_id = %s"), (snapshot_id,))
            if self.pedantic_validation:
                if self.__sid_in_table(snapshot_id, "public.exec_ready", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be removed from ER")
                if not self.__sid_in_table(snapshot_id, "public.busy_by_executor", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be added to EB")
            conn.commit()
        except Exception as e:
            F.print(f"exec checkout failed: {e}")
            last_e = e
            conn.rollback()
        if push_conn:
            self.pool.put_conn(conn)
        if last_e:
            raise last_e
        pkg_data = self.blob_storage.get(job.snapshot_id)
        pkg = Package()
        pkg.loadData(pkg_data)

        return job, pkg

    def on_ready_for_exec(self, pkg:Package, rank:int, label=NO_GROUP_DEFAULT, ex = {}, reuse_blob = False):
        if not self.connected():
            raise Exception("not connected")
        if not pkg or not pkg.isValid():
            raise ValueError("invalid package")
        tick = int(pkg.tick)
        sid = pkg.id()

        
        if (sid in self.blob_storage):
            if not reuse_blob:
                raise Exception(f"package [{sid}]already stored")
        else:
            _, jpkg = pkg.dump()
            sid = self.blob_storage.emplace(jpkg, sid)

        if sid not in self.blob_storage:
            raise Exception("object [{sid}] not saved")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False

        if self.__sid_in_table(sid, "public.analyze_ready", cur):
            raise Exception("object [{sid}] already in AR backlog")

        q = sql.SQL("""
            INSERT INTO public.exec_ready(
                snapshot_id, snapshot_group, rank, tick, ctime, ex) 
            VALUES (%s, %s, %s, %s, NOW(), %s);
        """)

        last_e = None
        try:
            cur.execute(q, (sid, label, rank, tick, F.jsump(ex)))
            conn.commit()
            if self.pedantic_validation and not self.__sid_in_table(sid, "public.exec_ready", cur):
                raise Exception("[PV] object [{sid}] already in ER backlog")
        except Exception as e:
            F.print(f"on_ready_for_exec failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e

    def undo_exec_checkout(self, snapshot_id):
        if not self.connected():
            raise Exception("not connected")
        if not snapshot_id:
            raise ValueError("no key")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        last_e = None
        try:
            if not self.__sid_in_table(snapshot_id, "public.busy_by_executor", cur):
                raise StorageKeyNotFoundError(snapshot_id, "EB")
            # move back to ready list
            cur.execute(sql.SQL("""
            INSERT INTO public.exec_ready ( 
                    task_id,
                    snapshot_id,
                    snapshot_group,
                    rank,
                    tick,
                    ctime,
                    ex
            )
            SELECT 
                public.busy_by_executor.task_id,
                public.busy_by_executor.snapshot_id,
                public.busy_by_executor.snapshot_group,
                public.busy_by_executor.rank,
                public.busy_by_executor.tick,
                public.busy_by_executor.ctime,
                public.busy_by_executor.ex
            FROM    public.busy_by_executor
            WHERE   public.busy_by_executor.snapshot_id = %s
            LIMIT 1;"""), (snapshot_id,))
            if cur.rowcount != 1:
                raise StorageIntegrityError(f"invalid task EB checkout undo. affected:{cur.rowcount} id:{snapshot_id}")
            # cleanup busy list
            cur.execute(sql.SQL("DELETE FROM public.busy_by_executor WHERE (snapshot_id=%s)"), (snapshot_id,))
            conn.commit()

            if self.pedantic_validation:
                if self.__sid_in_table(snapshot_id, "public.busy_by_executor", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be removed from EB")
                if not self.__sid_in_table(snapshot_id, "public.exec_ready", cur):
                    raise StorageIntegrityError(f"[PV] {snapshot_id} should be added to ER")

        except Exception as e:
            F.print(f"undo_exec_checkout [{snapshot_id}] failed: {e}")
            last_e = e
            conn.rollback()
        self.pool.put_conn(conn)
        if last_e:
            raise last_e

    def __get_top(self, table:str, count:int = 10, cur = None):
        if not self.connected():
            raise Exception("not connected")
        put_conn = False
        conn = None
        if not cur:
            conn = self.pool.get_conn()
            cur = conn.cursor()
            put_conn = True
        last_e = None
        rc_l = None
        try: #
            cur.execute(sql.SQL(f"""
                SELECT snapshot_id, rank
                FROM {table}
                ORDER BY rank DESC
                LIMIT %s; 
                """), (int(count),))
            rc_l = list(cur.fetchall())
        except Exception as e:
            F.print(f"top_ar failed: {e}")
            last_e = e
        if put_conn:
            self.pool.put_conn(conn)
        if last_e:
            raise last_e
        return rc_l
    
    def top_ar(self, count:int = 10, cur = None):
        return self.__get_top("public.analyze_ready", count, cur)
    def top_er(self, count:int = 10, cur = None):
        return self.__get_top("public.exec_ready", count, cur)

    def checkout_some_AR(self):
        if not self.connected():
            raise Exception("not connected")
        conn = self.pool.get_conn()
        cur = conn.cursor()
        conn.autocommit = False
        retry_count = 10
        top_count = 10
        ret_job = None
        ret_pkg = None
        while retry_count >= 0:
            l = self.top_ar(top_count, cur)
            if not l:
                raise StorageNoDataError("AR empty")
            candidate = random.choice(l)
            print(f"[{retry_count}] try candidate {candidate}")
            sid = candidate[0]
            if not sid:
                raise ValueError(f"no sid in {candidate}")
            try:
                ret_job, ret_pkg = self.checkout_analizer_job(sid)
            except (StorageIntegrityError, StorageKeyNotFoundError):
                retry_count -= 1
                continue
        if ret_pkg and ret_job:
            return ret_job, ret_pkg
        if retry_count <= 0:
            raise StorageConcurrencyError("AR co retry limit reached")
        
        # co data broken!
        raise ValueError("no job or pkg")
