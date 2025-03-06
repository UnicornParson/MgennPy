
import psycopg2
from psycopg2 import sql
from ..functional import F

class AnalizerJob():
    def __init__(self, task_id, snapshot_id, group, rank, tick, ctime, outputs, creator, exec_telemetry = {}, ex = {}):
        self.task_id = task_id
        self.snapshot_id = snapshot_id
        self.group = group
        self.rank = rank
        self.tick = tick
        self.ctime = ctime
        self.outputs = outputs
        self.creator = creator
        self.exec_telemetry = exec_telemetry
        self.ex = ex

    def isValid(self):
        return bool(self.snapshot_id) and bool(self.task_id)

    @staticmethod
    def from_query_row(row):
        return AnalizerJob(
            task_id=row[0],
            snapshot_id=row[1],
            group=row[2],
            rank=row[3],
            tick=row[4],
            ctime=row[5],
            outputs=row[6],
            creator=row[7],
            exec_telemetry=row[8],
            ex=row[9]
        )

    @staticmethod
    def from_db(table, snapshot_id, cur):
        #public.busy_by_analizer
        cur.execute(sql.SQL(f"SELECT * FROM {table} WHERE (snapshot_id = %s)" ), (snapshot_id,))
        row = cur.fetchone()
        if not row:
            F.print(f"job for {snapshot_id} not found in {table}")
            return None
        return AnalizerJob.from_query_row(row)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "snapshot_id": self.snapshot_id,
            "snapshot_group": self.group,
            "rank": self.rank,
            "tick": self.tick,
            "ctime": self.ctime,
            "outputs": self.outputs,
            "creator": self.creator,
            "exec_telemetry": self.exec_telemetry,
            "ex": self.ex
        }

    def __repr__(self):
        return f"Job(task_id={self.task_id}, snapshot_id=[{self.group}]{self.snapshot_id})"


class ExecutorJob():
    def __init__(self, task_id, snapshot_id, group, rank, tick, ctime, ex = {}):
        self.task_id = task_id
        self.snapshot_id = snapshot_id
        self.group = group
        self.rank = rank
        self.tick = tick
        self.ctime = ctime
        self.ex = ex

    def isValid(self):
        return bool(self.snapshot_id) and bool(self.task_id)

    @staticmethod
    def from_query_row(row):
        return ExecutorJob(
            task_id=row[0],
            snapshot_id=row[1],
            group=row[2],
            rank=row[3],
            tick=row[4],
            ctime=row[5],
            ex=row[6]
        )

    @staticmethod
    def from_db(table, snapshot_id, cur):
        cur.execute(sql.SQL(f"SELECT * FROM {table} WHERE (snapshot_id = %s)" ), (snapshot_id,))
        row = cur.fetchone()
        if not row:
            F.print(f"exec job for {snapshot_id} not found in {table}")
            return None
        return ExecutorJob.from_query_row(row)

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "snapshot_id": self.snapshot_id,
            "snapshot_group": self.group,
            "rank": self.rank,
            "tick": self.tick,
            "ctime": self.ctime,
            "ex": self.ex
        }

    def __repr__(self):
        return f"ExecJob(task_id={self.task_id}, snapshot_id=[{self.group}]{self.snapshot_id})"