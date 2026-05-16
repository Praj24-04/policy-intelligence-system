import psycopg2
import psycopg2.extras
import json

conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/policy_db",
                        cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

# Country breakdown
cur.execute("SELECT country, COUNT(*) as count FROM policies GROUP BY country ORDER BY count DESC")
rows = cur.fetchall()
print("COUNTRY COVERAGE:")
print("-" * 40)
total = 0
for r in rows:
    print(f"  {r['country']:30s}: {r['count']:>4}")
    total += r['count']
print(f"\n  {'TOTAL':30s}: {total:>4}")
print(f"  Countries represented: {len(rows)}")

# Region breakdown
cur.execute("SELECT region, COUNT(*) as count FROM policies GROUP BY region ORDER BY count DESC")
rows = cur.fetchall()
print(f"\nREGION COVERAGE:")
print("-" * 40)
for r in rows:
    print(f"  {r['region']:30s}: {r['count']:>4}")

# Sector breakdown
cur.execute("SELECT sector, COUNT(*) as count FROM policies GROUP BY sector ORDER BY count DESC")
rows = cur.fetchall()
print(f"\nSECTOR COVERAGE:")
print("-" * 40)
for r in rows:
    print(f"  {r['sector']:30s}: {r['count']:>4}")

# Source breakdown
cur.execute("SELECT CASE WHEN id LIKE 'eurlex_%' THEN 'EUR-Lex' WHEN id LIKE 'cisa_%' THEN 'CISA KEV' WHEN id LIKE 'fedreg_%' THEN 'Federal Register' ELSE 'Other' END as source, COUNT(*) as count FROM policies GROUP BY source ORDER BY count DESC")
rows = cur.fetchall()
print(f"\nSOURCE BREAKDOWN:")
print("-" * 40)
for r in rows:
    print(f"  {r['source']:30s}: {r['count']:>4}")

conn.close()
