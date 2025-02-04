import mcore as mc
from common import *
from common import storage as mstorage
import os
import socket
import pandas as pd

def example_save_pkg():
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.init()
    pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    pkg = mc.Package()
    pkg.loadFile(pkg_path)
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, df)

example_save_pkg()
# load run and save manally