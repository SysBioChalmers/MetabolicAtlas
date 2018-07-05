import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE


def connect(db_name='postgres', user=os.getenv('POSTGRES_USER'), host='db', password=os.getenv('POSTGRES_PASSWORD')):
    con = psycopg2.connect(dbname=db_name,
                           user= user, 
                           host=host,
                           password=password)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE
    return con

def execute(con, query):
    cur = con.cursor()
    cur.execute(query)
    return cur
