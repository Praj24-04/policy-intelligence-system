import sys
import sqlite3
import psycopg2
from pathlib import Path

_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.services.policy_fetcher import _classify_sector, _detect_country
from data.country_profiles import COUNTRY_PROFILES

def clean_database():
    print("Starting retrospective policy database cleanup...")
    
    # 1. Connect to PostgreSQL
    pg_conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/policy_db")
    pg_cur = pg_conn.cursor()
    
    # 2. Connect to SQLite
    sqlite_db = _backend_root / "data" / "policies.db"
    lite_conn = sqlite3.connect(sqlite_db)
    lite_conn.row_factory = sqlite3.Row
    lite_cur = lite_conn.cursor()
    
    # Fetch policies from PostgreSQL
    pg_cur.execute("SELECT id, title, sector, country, content FROM policies WHERE id LIKE 'fedreg_%' OR id LIKE 'eurlex_%'")
    pg_policies = pg_cur.fetchall()
    print(f"Fetched {len(pg_policies)} Federal Register/EUR-Lex policies from PostgreSQL.")
    
    pg_updated = 0
    pg_deleted = 0
    
    for row in pg_policies:
        pid, title, current_sector, current_country, content = row
        
        # Determine new sector
        new_sector = _classify_sector(title, content)
        
        # Determine new country
        new_country = _detect_country(title, content, hint=current_country)
        
        # If it doesn't fit any sector, delete it to maintain high quality
        if not new_sector:
            pg_cur.execute("DELETE FROM policies WHERE id = %s", (pid,))
            pg_deleted += 1
            print(f"  [PG DELETE] {pid}: {title[:60]}... (does not match any sector)")
            continue
            
        new_region = COUNTRY_PROFILES.get(new_country, {}).get("region", "Other")
        
        # If the country or sector changed, update it
        if new_sector != current_sector or new_country != current_country:
            pg_cur.execute("""
                UPDATE policies 
                SET sector = %s, country = %s, region = %s
                WHERE id = %s
            """, (new_sector, new_country, new_region, pid))
            pg_updated += 1
            print(f"  [PG UPDATE] {pid}: {title[:50]}... | Sector: {current_sector} -> {new_sector} | Country: {current_country} -> {new_country}")

    pg_conn.commit()
    print(f"PostgreSQL Cleanup Complete: {pg_updated} updated, {pg_deleted} deleted.")
    
    # Fetch policies from SQLite
    lite_policies = lite_cur.execute("SELECT id, title, sector, country, content FROM policies WHERE id LIKE 'fedreg_%' OR id LIKE 'eurlex_%'").fetchall()
    print(f"Fetched {len(lite_policies)} Federal Register/EUR-Lex policies from SQLite.")
    
    lite_updated = 0
    lite_deleted = 0
    
    for row in lite_policies:
        pid = row['id']
        title = row['title']
        current_sector = row['sector']
        current_country = row['country']
        content = row['content']
        
        new_sector = _classify_sector(title, content)
        new_country = _detect_country(title, content, hint=current_country)
        
        if not new_sector:
            lite_cur.execute("DELETE FROM policies WHERE id = ?", (pid,))
            lite_deleted += 1
            print(f"  [SQLITE DELETE] {pid}: {title[:60]}...")
            continue
            
        new_region = COUNTRY_PROFILES.get(new_country, {}).get("region", "Other")
        
        if new_sector != current_sector or new_country != current_country:
            lite_cur.execute("""
                UPDATE policies 
                SET sector = ?, country = ?, region = ?
                WHERE id = ?
            """, (new_sector, new_country, new_region, pid))
            lite_updated += 1
            print(f"  [SQLITE UPDATE] {pid}: {title[:50]}... | Sector: {current_sector} -> {new_sector} | Country: {current_country} -> {new_country}")
            
    lite_conn.commit()
    print(f"SQLite Cleanup Complete: {lite_updated} updated, {lite_deleted} deleted.")
    
    # Close connections
    pg_conn.close()
    lite_conn.close()
    print("All database cleanups complete!")

if __name__ == "__main__":
    clean_database()
