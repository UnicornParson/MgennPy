import pandas as pd
import random
from common import *
from common import storage as mstorage
import mcore as mc
import os
import inspect
from .utils import *

@W.timeit
def stats_only():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    print(f"stats: {storage.stats()}")
    F.set_print_token("")

@W.timeit
def example_labels():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    fill_count = 10
    lebel_before = storage.labels()
    sids, labels_added = fill_ar(storage, count=fill_count, randomize_labels=True)
    assert len(sids) == fill_count
    assert len(labels_added) == fill_count
    lebel_after = storage.labels()
    assert len(lebel_before) + len(labels_added) == len(lebel_after)

    # check snapshots
    for sid in sids:
        assert storage.find_snapshot(sid) != mstorage.StorageTable.Notable

    cleanup(sids, storage)
    F.set_print_token("")