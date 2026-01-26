import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os


load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")


conn = psycopg2.connect(
    dbname="postgres",
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
exists = cur.fetchone()

if not exists:
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    print(f"Database '{DB_NAME}' created successfully")
else:
    print(f"Database '{DB_NAME}' already exists")

cur.close()
conn.close()
