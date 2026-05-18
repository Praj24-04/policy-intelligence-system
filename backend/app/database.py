import psycopg2
import psycopg2.extras
import json
from pathlib import Path

DB_URL = "postgresql://postgres:admin123@localhost:5432/policy_db"

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        # sqlite uses ? for parameters, psycopg2 uses %s
        if params is not None and "?" in query:
             query = query.replace("?", "%s")
             
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_connection():
    conn = psycopg2.connect(DB_URL)
    return PostgresConnectionWrapper(conn)

def init_db():
    conn = get_connection()

    # ── Core policy tables ───────────────────────────────────────────────
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
            source_url  TEXT,
            key_requirements TEXT,
            timeline_phases TEXT,
            extracted_countries_cache TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS country_profiles (
            country             TEXT PRIMARY KEY,
            region              TEXT NOT NULL,
            gdp_tier            TEXT NOT NULL,
            regulatory_maturity TEXT NOT NULL,
            context             TEXT NOT NULL,
            priority_needs      TEXT,
            existing_sectors    TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS country_needs (
            country     TEXT PRIMARY KEY,
            description TEXT NOT NULL
        )
    """)

    # ── User authentication tables ───────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL PRIMARY KEY,
            email         TEXT UNIQUE NOT NULL,
            full_name     TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT DEFAULT 'user',
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id         SERIAL PRIMARY KEY,
            email      TEXT NOT NULL,
            token      TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used       BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── Per-user history tables ──────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_uploads (
            id           SERIAL PRIMARY KEY,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            filename     TEXT NOT NULL,
            title        TEXT,
            tags         TEXT,
            word_count   INTEGER,
            result_json  TEXT,
            created_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_generates (
            id           SERIAL PRIMARY KEY,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            country      TEXT NOT NULL,
            sector       TEXT NOT NULL,
            result_json  TEXT,
            created_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_compares (
            id           SERIAL PRIMARY KEY,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            policy_id_1  TEXT NOT NULL,
            policy_id_2  TEXT NOT NULL,
            result_json  TEXT,
            created_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] PostgreSQL Database initialized with auth + history tables")