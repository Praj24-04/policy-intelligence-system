import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from app.database import init_db, get_connection
from data.policies_seed import POLICIES


def seed():
    init_db()
    conn = get_connection()
    inserted = 0
    skipped = 0

    for p in POLICIES:
        try:
            cur = conn.execute("""
                INSERT INTO policies
                (id, title, sector, region, country, content, tags, status, year, version, source_url)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT (id) DO NOTHING
            """, (
                p["id"], p["title"], p["sector"], p["region"],
                p["country"], p["content"],
                json.dumps(p.get("tags", [])),
                p.get("status", "Active"),
                p.get("year"), p.get("version"),
                p.get("source_url", "")
            ))
            if cur.rowcount:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error inserting {p['id']}: {e}")
            skipped += 1

    conn.commit()
    conn.close()
    print(f"Seeded {inserted} policies | Skipped {skipped}")


if __name__ == "__main__":
    seed()
