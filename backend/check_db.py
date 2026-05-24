from app.database import get_connection
try:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]
    print(f"Count of policies in PostgreSQL table: {count}")
    
    # Let's print the first 3 policies to see if there is any data
    rows = conn.execute("SELECT id, title, sector, region, country FROM policies LIMIT 3").fetchall()
    print("Sample policies:")
    for r in rows:
        print(dict(r))
        
    conn.close()
except Exception as e:
    print(f"Error checking DB: {e}")
