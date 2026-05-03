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

    conn.commit()
    conn.close()
    print("✅ PostgreSQL Database initialized")