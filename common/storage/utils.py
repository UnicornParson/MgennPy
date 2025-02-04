import psycopg2
from psycopg2 import sql
from ..functional import F

class PGUtils():
    def table_exists(self, cur, table_name, schema_name='public'):
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s
            )
        """)
        cur.execute(query, (schema_name, table_name))
        exists = cur.fetchone()[0]
        return exists