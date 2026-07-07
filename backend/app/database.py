import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
import json
import hashlib
from pathlib import Path
from app.config import DATABASE_URL

# Centralized connection pool for database connections
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        try:
            # Min 2 connections, Max 20 connections for concurrency
            _pool = ThreadedConnectionPool(2, 20, dsn=DATABASE_URL)
        except Exception as e:
            print(f"[CRITICAL] Database connection pool failed to initialize: {e}")
            raise e
    return _pool

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        # Return connection to the central pool instead of closing it
        try:
            pool = get_pool()
            pool.putconn(self.conn)
        except Exception:
            # Fallback if pool is already cleaned up during shutdown
            self.conn.close()

def get_connection():
    pool = get_pool()
    conn = pool.getconn()
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id          SERIAL PRIMARY KEY,
            policy_id   TEXT NOT NULL,
            country     TEXT NOT NULL,
            helpful     INTEGER NOT NULL,
            comment     TEXT DEFAULT '',
            timestamp   TIMESTAMP DEFAULT NOW()
        )
    """)


    # ── Add pgvector columns (graceful if extension not available) ────
    try:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        conn.execute("ALTER TABLE policies ADD COLUMN IF NOT EXISTS embedding vector(768)")
        conn.execute("ALTER TABLE policies ADD COLUMN IF NOT EXISTS cluster_id integer")
        conn.execute("ALTER TABLE policies ADD COLUMN IF NOT EXISTS cluster_confidence double precision")
        conn.execute("ALTER TABLE policies ADD COLUMN IF NOT EXISTS embedding_model varchar(255)")
        conn.execute("ALTER TABLE policies ADD COLUMN IF NOT EXISTS last_embedded_at timestamp with time zone")
        conn.commit()
        print("[OK] pgvector columns added/verified")
    except Exception as e:
        print(f"[WARN] pgvector setup skipped (install pgvector extension for full ML): {e}")
        try:
            conn.conn.rollback()
        except Exception:
            pass

    # ── Database Indexes for Performance ───────────────────────────────
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_policies_sector ON policies(sector)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_policies_region ON policies(region)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_policies_year ON policies(year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_policies_country ON policies(country)")
        conn.commit()
        print("[OK] Database performance indexes verified/created")
    except Exception as ie:
        print(f"[WARN] Performance index creation skipped: {ie}")
        try:
            conn.conn.rollback()
        except Exception:
            pass

    conn.commit()
    conn.close()
    print("[OK] PostgreSQL Database initialized with auth + history tables")

    # ── Auto-seed foundational policies ─────────────────────────────────
    _seed_foundational_policies()
    _seed_country_data()


def _seed_foundational_policies():
    """Load foundational policies from JSON into the database if not already present."""
    data_file = Path(__file__).parent.parent / "data" / "foundational_policies.json"
    if not data_file.exists():
        print("[WARN] foundational_policies.json not found, skipping seed")
        return

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            policies = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to read foundational_policies.json: {e}")
        return

    conn = get_connection()
    inserted = 0
    for p in policies:
        try:
            existing = conn.execute(
                "SELECT id FROM policies WHERE id = %s", (p["id"],)
            ).fetchone()
            if existing:
                continue
            conn.execute("""
                INSERT INTO policies
                (id, title, sector, region, country, content, tags, status, year, version, source_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                p["id"], p["title"], p["sector"], p["region"],
                p["country"], p["content"],
                json.dumps(p.get("tags", [])),
                p.get("status", "Active"),
                p.get("year"),
                p.get("version", "1.0"),
                p.get("source_url", "")
            ))
            inserted += 1
        except Exception as e:
            print(f"  [WARN] Failed to seed policy {p.get('id')}: {e}")
            try:
                conn.conn.rollback()
            except Exception:
                pass

    if inserted > 0:
        conn.commit()
    conn.close()
    print(f"[OK] Foundational policies: {inserted} new, {len(policies) - inserted} existing")


def _seed_country_data():
    """Load and synchronize country profiles and needs into the database from country_profiles.py."""
    try:
        from data.country_profiles import COUNTRY_PROFILES
    except ImportError:
        print("[WARN] country_profiles.py not found, skipping country seed")
        return

    conn = get_connection()
    synced_profiles = 0
    synced_needs = 0

    for country, profile in COUNTRY_PROFILES.items():
        try:
            conn.execute("""
                INSERT INTO country_profiles
                (country, region, gdp_tier, regulatory_maturity, context, priority_needs, existing_sectors)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (country) DO UPDATE SET
                region = EXCLUDED.region,
                gdp_tier = EXCLUDED.gdp_tier,
                regulatory_maturity = EXCLUDED.regulatory_maturity,
                context = EXCLUDED.context,
                priority_needs = EXCLUDED.priority_needs,
                existing_sectors = EXCLUDED.existing_sectors
            """, (
                country,
                profile["region"],
                profile["gdp_tier"],
                profile["regulatory_maturity"],
                profile["context"],
                json.dumps(profile.get("priority_needs", [])),
                json.dumps(profile.get("existing_sectors", []))
            ))
            synced_profiles += 1
        except Exception as e:
            print(f"  [WARN] Failed to seed/sync profile for {country}: {e}")
            try:
                conn.conn.rollback()
            except Exception:
                pass

        # Also seed/sync country_needs with the context as description
        try:
            need_desc = profile.get("context", f"{country} regulatory needs")
            conn.execute("""
                INSERT INTO country_needs (country, description)
                VALUES (%s, %s)
                ON CONFLICT (country) DO UPDATE SET
                description = EXCLUDED.description
            """, (country, need_desc))
            synced_needs += 1
        except Exception as e:
            print(f"  [WARN] Failed to seed/sync need description for {country}: {e}")
            try:
                conn.conn.rollback()
            except Exception:
                pass

    conn.commit()
    conn.close()
    print(f"[OK] Country data synced: {synced_profiles} profiles, {synced_needs} needs updated in database")