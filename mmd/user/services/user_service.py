import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def get_users_psycopg():
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM user"
    cur.execute(query)
    if not cur:
        return None
    
    return cur.fetchall()
