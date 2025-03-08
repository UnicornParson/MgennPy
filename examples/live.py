import pandas as pd
import numpy as np
import random
from common import *
from common import storage as mstorage
import mcore as mc
import os
import inspect
from .utils import *
from .mock import *
from .push_and_save import *


@W.timeit
def example_core_life_cycle():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    fill_ar(storage, count=10, randomize_labels=True)
    cycle = mc.CoreLifeCycle()
    cycle.i_source = MockInputSource()
    cid, o_pkg = push_new_exec_ready(storage)
    job, pkg = storage.checkout_executor_job(cid)
    if not job or not isinstance(job, mstorage.ExecutorJob) or not job.isValid():
        raise ValueError("no exec job!")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    storage.undo_exec_checkout(cid)
    F.set_print_token("")

@W.timeit
def example_use_AR_top():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    F.print("init storage")
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    F.print("init storage - OK")
    sids, labels_added = fill_ar(storage, count=10, randomize_labels=True)
    F.print("fill storage - OK")
    F.table_print(storage.top_ar(10), ["snapshot_id", "rank"], title="TOP AR")
    F.table_print(storage.top_er(10), ["snapshot_id", "rank"], title="TOP ER")
    job, pkg = storage.checkout_some_AR()
    F.set_print_token("")
    if not job or not isinstance(job, mstorage.AnalizerJob) or not job.isValid():
        raise ValueError(f"no exec job! {type(job)} - {job}")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    F.print("select job - ok")
    ce = mc.Engine()
    ce.core = mc.Core()
    ce.core.load(pkg)
    ilabels = ce.core.input_names()
    F.print(f"found input names [{ilabels}]")
    ce.tick_offset = 0
    ticks = 12
    df_in = pd.DataFrame()
    if ilabels:
        df_in = pd.DataFrame(np.random.rand(len(ilabels)), columns=ilabels)
    df_out = pd.DataFrame()
    for t in range(ticks):
        row = pd.DataFrame()
        if ilabels:
            row = pd.DataFrame(np.random.rand(len(ilabels)), columns=ilabels)
        df_in = pd.concat([df_out, row], ignore_index=True)
        df_out = pd.concat([df_out, ce.run_once(df_in)], ignore_index=True)
    F.print(f"found some job {job} with pkg {pkg.id()}")
    cleanup(sids, storage)
    F.set_print_token("")