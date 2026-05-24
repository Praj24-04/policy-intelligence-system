from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database import get_connection

SECRET_KEY = "policysystem2024_jwt_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Password hashing ───────────────────────────────────────────────────────
# 4 rounds = fast for dev/demo. Bump to 10+ for production.
BCRYPT_ROUNDS = 4

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

# ── Token creation ─────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["type"] = "access"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_reset_token(email: str) -> str:
    payload = {
        "sub": email,
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> str | None:
    """Returns email if valid reset token, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None

# ── DB helpers ─────────────────────────────────────────────────────────────
def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, email, full_name, password_hash, role, created_at FROM users WHERE email = %s",
        (email.lower(),)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, email, full_name, password_hash, role, created_at FROM users WHERE id = %s",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

# ── Dependency ─────────────────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    debug_log_path = r"D:\VIT\PROJECTS\POLICY_PROJECT\backend\auth_debug.log"
    try:
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- get_current_user called at {datetime.utcnow()} ---\n")
            f.write(f"Received Token: '{token}'\n")
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"Decoded Payload: {payload}\n")
            
        if payload.get("type") != "access":
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write("Error: Invalid token type\n")
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        user_id = payload.get("sub")
        if not user_id:
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write("Error: Invalid token sub\n")
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user = get_user_by_id(int(user_id))
        if not user:
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write(f"Error: User not found for id {user_id}\n")
            raise HTTPException(status_code=401, detail="User not found")
            
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write("Token verification successful!\n\n")
        return user
    except JWTError as e:
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"JWTError raised: {str(e)}\n\n")
        raise HTTPException(status_code=401, detail="Invalid or expired token")