from app.database import get_connection
conn = get_connection()
rows = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name").fetchall()
conn.close()
for r in rows:
    print(r[0])
