from app.database import get_connection

conn = get_connection()
rows = conn.execute("SELECT id, email, role, password_hash FROM users WHERE role = 'admin'").fetchall()
print("Admin users found:")
for r in rows:
    print(dict(r))
conn.close()
