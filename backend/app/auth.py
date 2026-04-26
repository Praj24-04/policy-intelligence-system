from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "policysystem2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

USERS = {
    "admin": {
        "username": "admin",
        "password": "policy2024",
        "role": "admin",
        "full_name": "System Administrator"
    },
    "analyst": {
        "username": "analyst",
        "password": "analyst2024",
        "role": "analyst",
        "full_name": "Policy Analyst"
    }
}

def verify_password(plain: str, username: str) -> bool:
    user = USERS.get(username)
    if not user:
        return False
    return plain == user["password"]

def create_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        return USERS[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")