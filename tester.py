import mcore as mc
from common import *

db_conf = PG_Pool.db_conf_from_env()
pool = PG_Pool(db_conf)
storage = MgennStorage(pool)
storage.init()