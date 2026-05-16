"""
Clean the database of all old hardcoded/seeded policies.
Removes everything that wasn't fetched from a live API.
After this, only eurlex_, cisa_, and fedreg_ prefixed policies remain.
"""
import psycopg2
import psycopg2.extras

DB_URL = "postgresql://postgres:admin123@localhost:5432/policy_db"

conn = psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

# Count what we have
cur.execute("SELECT COUNT(*) as total FROM policies")
total = cur.fetchone()["total"]

cur.execute("SELECT COUNT(*) FROM policies WHERE id LIKE 'eurlex_%'")
eurlex = cur.fetchone()["count"]

cur.execute("SELECT COUNT(*) FROM policies WHERE id LIKE 'cisa_%'")
cisa = cur.fetchone()["count"]

cur.execute("SELECT COUNT(*) FROM policies WHERE id LIKE 'fedreg_%'")
fedreg = cur.fetchone()["count"]

old = total - eurlex - cisa - fedreg

print(f"Current DB state:")
print(f"  Total:            {total}")
print(f"  EUR-Lex (live):   {eurlex}")
print(f"  CISA (live):      {cisa}")
print(f"  Fed Register:     {fedreg}")
print(f"  OLD/hardcoded:    {old}")
print()

if old > 0:
    print(f"Deleting {old} old hardcoded/seeded policies...")
    cur.execute("""
        DELETE FROM policies 
        WHERE id NOT LIKE 'eurlex_%' 
        AND id NOT LIKE 'cisa_%' 
        AND id NOT LIKE 'fedreg_%'
    """)
    conn.commit()
    print(f"  Deleted {cur.rowcount} rows.")
else:
    print("No old policies to clean.")

# Also clear NER cache for deleted policies
cur.execute("""
    UPDATE policies SET extracted_countries_cache = NULL
""")
conn.commit()
print("NER cache cleared (will re-warm on next startup).")

# Final count
cur.execute("SELECT COUNT(*) as total FROM policies")
final = cur.fetchone()["total"]
print(f"\nFinal DB state: {final} policies (all live-fetched)")

conn.close()
