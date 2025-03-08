import pandas as pd
import random
from common import *
from common import storage as mstorage
import mcore as mc
import os
import inspect
from .utils import *

@W.timeit
def push_new_exec_done(storage):
    pkg = mc.Package()
    pkg.loadFile(f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg")
    cid = pkg.renew_id()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, make_in_df())
    return cid, pkg

@W.timeit
def push_new_exec_ready(storage):
    pkg = mc.Package()
    pkg.loadFile(f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg")
    cid = pkg.renew_id()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_ready_for_exec(pkg, 33)
    return cid, pkg

@W.timeit
def example_save_pkg():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    pkg = mc.Package()
    pkg.loadFile(pkg_path)
    df = make_in_df()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, df)
    F.set_print_token("")

@W.timeit
def example_analyzer_checkout():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()

    # make new unic snapshot and save
    pkg = PackageUtils.makeRandomContent(mc.Package.make_empty(), PkgSizePreset.Small)
    df = make_in_df()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, df)

    # checkout it
    print(f"db stats (before_co) {storage.stats()}")
    job, pkg = storage.checkout_analizer_job(sid)
    if not job or not isinstance(job, mstorage.AnalizerJob) or not job.isValid():
        raise ValueError("no job!")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    pkg.pretty_print()
    print(f"#1 has a job! {job}. sid in {storage.find_snapshot(job.snapshot_id).value}")
    print(f"#2 has a pkg! sz:{len(pkg)}")
    print(f"db stats (after co){storage.stats()}")
    storage.undo_analyzer_checkout(job.snapshot_id)
    print(f"#3 undo ok sid in {storage.find_snapshot(job.snapshot_id).value}")
    print(f"db stats {storage.stats()}")
    F.set_print_token("")