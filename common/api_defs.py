from enum import Enum

class ApiTag:
    TAG_META = "meta"
    TAG_CONTENT = "content"
    TAG_STATE = "state"
    TAG_COMMENT = "comment"
    TAG_CMD = "cmd"
    TAG_ORIGINATOR = "originator"
    TAG_TOKEN = "token"
    TAG_ARGS = "args"
    TAG_ALIAS = "alias"
    TAG_NAME = "name"
    TAG_PROCESSINGTIME = "queryduration"
    TAG_SNAPSHOTSCOUNT = "snapshotscount"
    TAG_ALIASESCOUNT = "aliasescount"
    TAG_BLSIZE = "blsize"
    TAG_RESP_CODE = "resp"
    TAG_OWNER = "owner"
    TAG_SNAPSHOT_NAME = "snapshotname"
    TAG_SNAPSHOT_REV = "rev"
    TAG_DELTA_NAME = "delta"
    TAG_HASH = "hash"
    TAG_LIST = "list"
    TAG_ID = "id"
    TAG_FILTER_NAME = "filter"
    TAG_FILTER_MOD = "mod"
    TAG_FILTER_ARGS = TAG_ARGS


class ApiValus:
    VALUE_YES = "y"
    VALUE_NO = "n"

class ApiRespState:
    RESP_STATE_OK = "OK"
    RESP_STATE_NOTFOUND = "not found"
    RESP_STATE_DBERROR = "DB error"
    RESP_STATE_ARG = "invalid argument"
    RESP_STATE_ENGINE_ERROR = "engine error"
    RESP_STATE_UNKNOWN = "unknown"
    RESP_STATE_INVALID_RESPONCE = "invalid responce"

class ApiCmd:
    CMD_GET_SNAPSHOTS_LIST = "getshapshotlist"
    CMD_GET_SNAPSHOT = "getshapshot"
    CMD_GET_STAT = "getstat"
    CMD_GET_LAST_REV = "getlastrev"

    CMD_SET_SNAPSHOT_STATE = "setsnapshotstate"
    CMD_SAVE_SNAPSHOT = "savesnapshot"
    CMD_POST_TEST = "postecho"

    CMD_ALIAS_EXISTS = "alias.exists"
    CMD_ALIAS_RESOLVE = "alias.resolve"
    CMD_ALIAS_GET = "alias.get"
    CMD_ALIAS_LIST = "alias.list"

    CMD_BL_ASSIGN = "bl.assign"
    CMD_BL_LIST = "bl.list"
    CMD_BL_SET_STATE = "bl.setstate"
    CMD_BL_LIST_SIZE = "bl.listsize"
    CMD_BL_SET = "bl.set"

class ApiAdminCmd:
    CMD_GET_SNAPSHOTS_LIST = "admin.getshapshotlist"
        

class BlState:
    BLSTATE_FREE = "free"
    BLSTATE_NULL = "null"
    BLSTATE_ASSIGNED = "assigned"
    BLSTATE_FAILED = "failed"
    BLSTATE_DONE = "done"

class ListFilter:
    LISTFILTER_OWNER = "owner"
    LISTFILTER_STATE = "state"
    LISTFILTER_HASH = "hash"

class ListFilterMod:
    LISTFILTER_MOD_FIRST = "first"
    LISTFILTER_MOD_LAST = "last"

class SnapshotState:
    SNAPSHOT_STATE_NEW = "new"
    SNAPSHOT_STATE_INPROGRESS = "inprogress"
    SNAPSHOT_STATE_RESERVED = "reserved"
    SNAPSHOT_STATE_READY = "ready"
    SNAPSHOT_STATE_DEAD = "dead"
    SNAPSHOT_STATE_ERROR_INTERNAL = "internalerror"
    SNAPSHOT_STATE_ERROR_INVALID = "invalid"