from app.database import get_connection

conn = get_connection()
conn.execute("DELETE FROM policies WHERE id LIKE 'live_%'")
conn.commit()
print('Deleted old live policies')
conn.close()
