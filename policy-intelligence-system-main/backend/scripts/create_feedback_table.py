import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_connection

conn = get_connection()
conn.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id TEXT NOT NULL,
        country TEXT NOT NULL,
        helpful INTEGER NOT NULL,
        comment TEXT DEFAULT '',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
print('Feedback table created')
conn.close()