import json
import hashlib
from datetime import datetime
from pathlib import Path
from app.database import get_connection

def generate_id(title: str, country: str) -> str:
    raw = f"{title.lower().strip()}{country.lower().strip()}"
    return "live_" + hashlib.md5(raw.encode()).hexdigest()[:8]

def policy_exists(policy_id: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT id FROM policies WHERE id = ?", (policy_id,)).fetchone()
    conn.close()
    return row is not None

def save_policy(policy: dict) -> bool:
    if policy_exists(policy["id"]):
        return False
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO policies 
            (id, title, sector, region, country, content, tags, status, year, version, source_url)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            policy["id"], policy["title"], policy["sector"], policy["region"],
            policy["country"], policy["content"], json.dumps(policy.get("tags", [])),
            policy.get("status", "Active"), policy.get("year"),
            policy.get("version", "1.0"), policy.get("source_url", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        conn.close()
        return False

def run_full_fetch() -> dict:
    print("\nStarting simulated live policy stream pipeline...")
    print("=" * 50)

    # Path to our massive simulated live stream
    stream_file = Path(__file__).parent.parent.parent / "data" / "global_policies_stream.json"
    
    all_policies = []
    if stream_file.exists():
        with open(stream_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_policies = data.get("policies", [])
            for p in raw_policies:
                # Add generated ID
                p["id"] = generate_id(p["title"], p["country"])
                all_policies.append(p)
    else:
        print("Data stream file not found.")

    print(f"\nTotal pulled from stream: {len(all_policies)}")

    inserted = 0
    duplicates = 0
    for policy in all_policies:
        if save_policy(policy):
            inserted += 1
        else:
            duplicates += 1

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_fetched": len(all_policies),
        "inserted": inserted,
        "duplicates_skipped": duplicates,
        "sources": ["Global JSON Stream"]
    }

    print(f"Inserted: {inserted} new policies")
    print(f"Skipped: {duplicates} duplicates")
    print("=" * 50)
    return summary

def get_fetch_status() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]
    live = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE id LIKE 'live_%'"
    ).fetchone()[0]
    sectors = conn.execute(
        "SELECT sector, COUNT(*) as count FROM policies GROUP BY sector"
    ).fetchall()
    conn.close()
    return {
        "total_policies": total,
        "live_fetched": live,
        "curated": total - live,
        "sectors": {r["sector"]: r["count"] for r in sectors},
        "last_updated": datetime.now().isoformat()
    }