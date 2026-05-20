import os
import sys
import psycopg2

# Adjust sys.path to allow importing from the app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.database import DB_URL
except ImportError:
    DB_URL = "postgresql://postgres:admin123@localhost:5432/policy_db"

def run_migration():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    migration_file = os.path.abspath(os.path.join(script_dir, "..", "migrations", "add_pgvector.sql"))
    
    if not os.path.exists(migration_file):
        print(f"[ERROR] Migration file not found at: {migration_file}")
        sys.exit(1)

    print(f"Reading migration script: {migration_file}...")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql = f.read()

    # Mask credentials for logging
    db_host_info = DB_URL.split("@")[-1] if "@" in DB_URL else "localhost"
    print(f"Connecting to database at: {db_host_info}...")
    
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Applying migration inside transaction block...")
        cur.execute(sql)
        
        # Commit if successful
        conn.commit()
        print("[SUCCESS] Database migration applied successfully!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        if conn:
            print("Rolling back transaction to keep database in safe state...")
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
