import psycopg2, psycopg2.extras
conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/policy_db",
                        cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()
cur.execute("SELECT title FROM policies WHERE sector = 'POSH Policies' ORDER BY title")
rows = cur.fetchall()
print(f"POSH Policies: {len(rows)}\n")
for r in rows:
    print(f"  {r['title'][:120]}")
conn.close()
