import os
import psycopg2
from dotenv import load_dotenv
from django.contrib.auth.hashers import make_password, check_password

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT id_user, email, password_hash FROM users WHERE email=%s"
    cur.execute(query, (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None

    if check_password(password, user[2]):
        return {"id": user[0], "email": user[1]}

    return None


def register_user(name, surname, email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT email FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False

    cur.execute(
        "INSERT INTO users (name, surname, email, password_hash, role) VALUES (%s,%s,%s,%s,%s)",
        (name, surname, email, make_password(password), "user")
    )

    conn.commit()
    cur.close()
    conn.close()
    return True
