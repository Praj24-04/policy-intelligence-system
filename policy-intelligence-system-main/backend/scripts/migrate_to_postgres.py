import sys
from pathlib import Path
import sqlite3
import json

_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection, init_db
from data.country_profiles import COUNTRY_PROFILES

COUNTRY_NEED_DESCRIPTIONS = {
    "Indonesia": "Indonesia urgently needs cybersecurity incident response laws...",
    "Nigeria": "Nigeria needs financial cybersecurity standards...",
    "Kenya": "Kenya needs data privacy legislation...",
    "Saudi Arabia": "Saudi Arabia needs AI governance frameworks...",
    "United Arab Emirates": "UAE needs data privacy legislation...",
    "South Korea": "South Korea needs comprehensive data privacy rights...",
    "Argentina": "Argentina needs AI governance frameworks...",
    "Brazil": "Brazil needs mandatory cybersecurity incident...",
    "Mexico": "Mexico needs cybersecurity standards...",
    "India": "India needs mandatory cybersecurity incident reporting...",
    "Japan": "Japan needs binding AI safety requirements...",
    "Australia": "Australia needs privacy law reform...",
    "Canada": "Canada needs mandatory cybersecurity incident reporting...",
    "South Africa": "South Africa needs cybersecurity incident response...",
    "United Kingdom": "UK needs AI liability legislation...",
    "Germany": "Germany needs AI quality standards...",
    "France": "France needs binding AI accountability rules...",
    "Singapore": "Singapore needs quantum-resilient cybersecurity...",
    "China": "China needs international AI safety alignment...",
    "United States": "United States needs federal privacy legislation...",
    "European Union": "European Union needs AI Act enforcement...",
    "International": "International bodies need global AI governance..."
}

def migrate():
    print("🚀 Initializing PostgreSQL Database Schema...")
    init_db()
    
    print("🚀 Migrating Data from SQLite to PostgreSQL...")
    sqlite_db = _backend_root / "data" / "policies.db"
    
    if not sqlite_db.exists():
        print("❌ SQLite database not found. Skipping policy migration.")
        return
        
    old_conn = sqlite3.connect(sqlite_db)
    old_conn.row_factory = sqlite3.Row
    
    # Check if 'extracted_countries_cache' exists in sqlite
    has_cache = False
    try:
        old_conn.execute("SELECT extracted_countries_cache FROM policies LIMIT 1")
        has_cache = True
    except sqlite3.OperationalError:
        pass

    rows = old_conn.execute("SELECT * FROM policies").fetchall()
    old_conn.close()
    
    pg_conn = get_connection()
    
    print(f"📦 Found {len(rows)} policies in SQLite. Inserting into PostgreSQL...")
    for row in rows:
        p = dict(row)
        try:
            cache_val = p.get('extracted_countries_cache') if has_cache else None
            
            pg_conn.execute("""
                INSERT INTO policies (id, title, sector, region, country, content, tags, status, year, version, source_url, extracted_countries_cache)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                p['id'], p['title'], p['sector'], p['region'], p['country'],
                p['content'], p['tags'], p.get('status', 'Active'), p.get('year'),
                p.get('version'), p.get('source_url'), cache_val
            ))
        except Exception as e:
            print(f"⚠️ Error inserting policy {p['id']}: {e}")

    print("🌍 Inserting Country Profiles...")
    for country, profile in COUNTRY_PROFILES.items():
        try:
            pg_conn.execute("""
                INSERT INTO country_profiles (country, region, gdp_tier, regulatory_maturity, context, priority_needs, existing_sectors)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (country) DO NOTHING
            """, (
                country,
                profile.get('region', ''),
                profile.get('gdp_tier', ''),
                profile.get('regulatory_maturity', ''),
                profile.get('context', ''),
                json.dumps(profile.get('priority_needs', [])),
                json.dumps(profile.get('existing_sectors', []))
            ))
        except Exception as e:
            print(f"⚠️ Error inserting profile for {country}: {e}")

    print("📖 Inserting Country Needs...")
    for country, need_desc in COUNTRY_NEED_DESCRIPTIONS.items():
        try:
            pg_conn.execute("""
                INSERT INTO country_needs (country, description)
                VALUES (%s, %s)
                ON CONFLICT (country) DO NOTHING
            """, (country, need_desc))
        except Exception as e:
            print(f"⚠️ Error inserting needs for {country}: {e}")

    pg_conn.commit()
    pg_conn.close()
    print("✅ Migration Complete!")

if __name__ == "__main__":
    migrate()
