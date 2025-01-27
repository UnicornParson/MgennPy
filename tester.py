import mcore as mc
from common import *

db_conf = ObjectStorage.db_conf_from_env()

storage = MgennStorage(db_conf)
storage.init()