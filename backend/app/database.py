import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "policies.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            sector      TEXT NOT NULL,
            region      TEXT NOT NULL,
            country     TEXT NOT NULL,
            content     TEXT NOT NULL,
            tags        TEXT,
            status      TEXT DEFAULT 'Active',
            year        INTEGER,
            version     TEXT,
            source_url  TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized")