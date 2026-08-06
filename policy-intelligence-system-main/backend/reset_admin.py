from app.database import get_connection
from app.auth import hash_password

new_hash = hash_password("Admin@123456")
conn = get_connection()
conn.execute(
    "UPDATE users SET password_hash = %s WHERE email = %s",
    (new_hash, "admin@policyiq.com")
)
conn.commit()
conn.close()
print("Admin password reset to: Admin@123456")
