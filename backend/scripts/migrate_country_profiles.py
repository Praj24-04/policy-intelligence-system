import sys
import json
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from data.country_profiles import COUNTRY_PROFILES

def migrate():
    print("[MIGRATION] Starting country profiles migration...")
    conn = get_connection()
    try:
        # Create table if not exists (in case)
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
        conn.commit()

        # Insert / Upsert entries
        for country, data in COUNTRY_PROFILES.items():
            p_needs_str = json.dumps(data.get("priority_needs", []))
            e_sectors_str = json.dumps(data.get("existing_sectors", []))
            
            conn.execute("""
                INSERT INTO country_profiles (country, region, gdp_tier, regulatory_maturity, context, priority_needs, existing_sectors)
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
                data.get("region"),
                data.get("gdp_tier"),
                data.get("regulatory_maturity"),
                data.get("context"),
                p_needs_str,
                e_sectors_str
            ))
        conn.commit()
        print(f"[MIGRATION] Successfully migrated {len(COUNTRY_PROFILES)} country profiles.")
    except Exception as e:
        print(f"[MIGRATION] Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
