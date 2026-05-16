import psycopg2
conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/policy_db")
cur = conn.cursor()
cur.execute("DELETE FROM policies WHERE id LIKE 'fedreg_%'")
conn.commit()
print(f"Deleted {cur.rowcount} fedreg policies for re-fetch with country tagging")
conn.close()
