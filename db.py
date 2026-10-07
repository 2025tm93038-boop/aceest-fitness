"""
ACEest Fitness & Gym - persistence layer.
Version 2.0: SQLite-backed client storage.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "aceest_fitness.db"


def get_connection(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            program TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin'
        )
    """)
    cur.execute("SELECT 1 FROM users WHERE username = 'admin'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin"),
        )
    conn.commit()
    conn.close()


def add_client(name, program, db_path=None):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO clients (name, program) VALUES (?, ?)",
        (name, program),
    )
    conn.commit()
    conn.close()


def get_client(name, db_path=None):
    conn = get_connection(db_path)
    row = conn.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_clients(db_path=None):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def verify_user(username, password, db_path=None):
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
