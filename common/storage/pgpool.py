import psycopg2
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool
from ..functional import F

class PG_Pool:
    def __init__(self, db_conf):
        host, user, password, dbname = db_conf
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # min connections
            20,  # max connections
            user=user,
            password=password,
            host=host,
            port=5432,
            database=dbname
        )

    def __del__(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None

    def __exit__(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None

    @staticmethod
    def db_conf_from_env():
        # return db_host, db_user, db_password, db_name
        env = F.get_env(['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'])
        db_host = env['DB_HOST']
        db_user = env['DB_USER']
        db_password = env['DB_PASSWORD']
        db_name = env['DB_NAME']
        return (db_host, db_user, db_password, db_name)

    def connected(self) -> bool:
        return bool(self.connection_pool) and not self.connection_pool.closed 

    def get_conn(self):
        return self.connection_pool.getconn()

    def put_conn(self, conn):
        return self.connection_pool.putconn(conn)