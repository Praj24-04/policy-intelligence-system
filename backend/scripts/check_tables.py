import os
import sys
import psycopg2

# Adjust path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import DATABASE_URL
except ImportError:
    DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/policy_db"

def check_tables():
    required_tables = [
        "policies",
        "country_profiles",
        "country_needs",
        "users",
        "password_reset_tokens",
        "user_uploads",
        "user_generates",
        "user_compares",
        "feedback"
    ]
    
    print("=" * 60)
    print("POLICYIQ DATABASE TABLE VERIFICATION SCRIPT")
    print("=" * 60)
    
    # Mask credentials for display
    db_host_info = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "localhost"
    print(f"Connecting to database: {db_host_info}...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Verify pgvector extension
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cur.fetchone()
        vector_status = "INSTALLED (✅)" if vector_ext else "NOT INSTALLED (❌)"
        print(f"pgvector Extension: {vector_status}")
        print("-" * 60)
        
        print(f"{'Table Name':<25} | {'Status':<12} | {'Row Count':<10}")
        print("-" * 60)
        
        for table in required_tables:
            try:
                # Check if table exists
                cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                exists = cur.fetchone()[0]
                
                if exists:
                    # Get row count
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cur.fetchone()[0]
                    status = "EXISTS (✅)"
                else:
                    status = "MISSING (❌)"
                    count = 0
                    
                print(f"{table:<25} | {status:<12} | {count:<10}")
            except Exception as table_err:
                print(f"{table:<25} | ERROR (❌)    | N/A")
                conn.rollback()
                
        print("=" * 60)
        
    except Exception as conn_err:
        print(f"[CRITICAL ERROR] Failed to connect to database: {conn_err}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_tables()
