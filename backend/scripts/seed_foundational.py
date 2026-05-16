import json
import psycopg2
import psycopg2.extras
import os
from pathlib import Path

# Connect to database
try:
    conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/policy_db")
    cur = conn.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(1)

# Ensure the policies table exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id VARCHAR PRIMARY KEY,
        title VARCHAR NOT NULL,
        sector VARCHAR NOT NULL,
        region VARCHAR,
        country VARCHAR,
        content TEXT NOT NULL,
        tags VARCHAR[],
        status VARCHAR,
        year INTEGER,
        version VARCHAR,
        source_url VARCHAR
    )
""")

# Load foundational policies
data_file = Path(__file__).parent.parent / "data" / "foundational_policies.json"
try:
    with open(data_file, "r", encoding="utf-8") as f:
        policies = json.load(f)
except Exception as e:
    print(f"Error loading {data_file}: {e}")
    exit(1)

# Ingest into database
inserted_count = 0
for policy in policies:
    try:
        cur.execute(
            """
            INSERT INTO policies (id, title, sector, region, country, content, tags, status, year, version, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                sector = EXCLUDED.sector,
                region = EXCLUDED.region,
                country = EXCLUDED.country,
                content = EXCLUDED.content,
                tags = EXCLUDED.tags,
                status = EXCLUDED.status,
                year = EXCLUDED.year,
                version = EXCLUDED.version,
                source_url = EXCLUDED.source_url
            """,
            (
                policy["id"], policy["title"], policy["sector"], policy["region"],
                policy["country"], policy["content"], policy.get("tags", []),
                policy.get("status", "Active"), policy.get("year"),
                policy.get("version", "1.0"), policy.get("source_url")
            )
        )
        inserted_count += 1
    except Exception as e:
        print(f"Error inserting policy {policy['id']}: {e}")
        conn.rollback()

conn.commit()
print(f"Successfully seeded {inserted_count} foundational policies into the database.")

cur.execute("SELECT COUNT(*) FROM policies")
total_policies = cur.fetchone()[0]
print(f"Total policies in database: {total_policies}")

cur.close()
conn.close()
