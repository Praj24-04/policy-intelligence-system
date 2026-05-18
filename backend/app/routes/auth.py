from fastapi import APIRouter, Depends, HTTPException
from app.auth import (
    hash_password, verify_password,
    create_access_token, create_reset_token, verify_reset_token,
    get_current_user, get_user_by_email
)
from app.database import get_connection
from app.email_service import send_reset_email
from app.models.schemas import (
    RegisterRequest, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    TokenResponse, UserOut
)
from datetime import datetime

router = APIRouter()

# ── Register ────────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    email = req.email.lower()

    # Check if already registered
    existing = get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    if len(req.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters.")

    pw_hash = hash_password(req.password)

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (email, full_name, password_hash) VALUES (%s, %s, %s) RETURNING id, email, full_name, role, created_at",
        (email, req.full_name.strip(), pw_hash)
    )
    row = dict(cur.fetchone())
    conn.commit()
    conn.close()

    token = create_access_token({"sub": str(row["id"]), "role": row["role"]})
    return TokenResponse(
        access_token=token,
        user=UserOut(**row)
    )

# ── Login ───────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = get_user_by_email(req.email.lower())
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            created_at=user["created_at"]
        )
    )

# ── Me ──────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    return UserOut(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        created_at=current_user.get("created_at")
    )

# ── Forgot Password ─────────────────────────────────────────────────────────
@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    email = req.email.lower()
    user = get_user_by_email(email)

    # Always return 200 to prevent email enumeration attacks
    if not user:
        return {"message": "If that email is registered, a reset link has been sent."}

    token = create_reset_token(email)

    # Store token in DB
    conn = get_connection()
    from datetime import timedelta
    expires = datetime.utcnow() + timedelta(hours=1)
    conn.execute(
        "INSERT INTO password_reset_tokens (email, token, expires_at) VALUES (%s, %s, %s)",
        (email, token, expires)
    )
    conn.commit()
    conn.close()

    send_reset_email(email, token)
    return {"message": "If that email is registered, a reset link has been sent."}

# ── Reset Password ──────────────────────────────────────────────────────────
@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    email = verify_reset_token(req.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters.")

    # Check token hasn't been used
    conn = get_connection()
    row = conn.execute(
        "SELECT id, used FROM password_reset_tokens WHERE token = %s AND email = %s",
        (req.token, email)
    ).fetchone()

    if not row or row["used"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Reset link already used or invalid.")

    # Mark token as used and update password
    new_hash = hash_password(req.new_password)
    conn.execute("UPDATE password_reset_tokens SET used = TRUE WHERE id = %s", (row["id"],))
    conn.execute("UPDATE users SET password_hash = %s WHERE email = %s", (new_hash, email))
    conn.commit()
    conn.close()

    return {"message": "Password updated successfully. You can now log in."}

# ── User History ────────────────────────────────────────────────────────────
@router.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    uid = current_user["id"]
    conn = get_connection()

    uploads = conn.execute(
        "SELECT id, filename, title, word_count, created_at FROM user_uploads WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (uid,)
    ).fetchall()

    generates = conn.execute(
        "SELECT id, country, sector, created_at FROM user_generates WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (uid,)
    ).fetchall()

    compares = conn.execute(
        "SELECT id, policy_id_1, policy_id_2, created_at FROM user_compares WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (uid,)
    ).fetchall()

    conn.close()
    return {
        "uploads":   [dict(r) for r in uploads],
        "generates": [dict(r) for r in generates],
        "compares":  [dict(r) for r in compares],
    }

# ── Logout (client-side only, kept for API completeness) ────────────────────
@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}