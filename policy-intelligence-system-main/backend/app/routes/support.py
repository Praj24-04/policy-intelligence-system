import time
from collections import defaultdict
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.auth import get_current_user, require_admin
from app.database import get_connection
from app.limiter import limiter

router = APIRouter()

# Simple sliding-window in-memory rate limiter per user for support messages
# Limits each user to a max number of messages in a time window
USER_MESSAGE_TIMESTAMPS = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
MAX_MESSAGES_PER_WINDOW = 10


def check_user_rate_limit(user_id: int):
    now = time.time()
    user_times = USER_MESSAGE_TIMESTAMPS[user_id]
    # Filter out timestamps older than the sliding window
    valid_times = [t for t in user_times if now - t < RATE_LIMIT_WINDOW]
    USER_MESSAGE_TIMESTAMPS[user_id] = valid_times

    if len(valid_times) >= MAX_MESSAGES_PER_WINDOW:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before sending another support message."
        )
    USER_MESSAGE_TIMESTAMPS[user_id].append(now)


# ── Schemas ────────────────────────────────────────────────────────────────
class SupportMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Support message content")

class AdminReplyCreate(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1, max_length=2000, description="Admin reply content")

class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(open|resolved)$", description="Conversation status ('open' or 'resolved')")


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/messages")
@limiter.limit("15/minute")
def create_support_message(
    payload: SupportMessageCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Client endpoint to submit a support query.
    SECURITY & PRIVACY:
    - User identity (user_id) is strictly derived from the validated JWT token (current_user["id"]).
    - Request payload is validated using Pydantic (max 2000 chars, non-empty).
    - Database query uses parameterized execution (%s).
    - Per-user rate limiting is enforced.
    """
    client_user_id = current_user["id"]
    check_user_rate_limit(client_user_id)

    msg_text = payload.message.strip()
    if not msg_text:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO support_messages (user_id, message, sender, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, message, sender, status, created_at
            """,
            (client_user_id, msg_text, "client", "open")
        )
        conn.commit()
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()


@router.get("/messages")
def get_user_support_messages(
    current_user: dict = Depends(get_current_user)
):
    """
    Client endpoint to fetch their own support conversation.
    SECURITY & PRIVACY:
    - IDOR Prevention: Filter strictly by JWT user_id (current_user["id"]).
      Client cannot pass a user_id parameter to view other users' messages.
    """
    client_user_id = current_user["id"]
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, user_id, message, sender, status, created_at
            FROM support_messages
            WHERE user_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (client_user_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/admin/messages")
def get_admin_support_messages(
    current_user: dict = Depends(require_admin)
):
    """
    Admin endpoint to view support threads for all users.
    SECURITY & PRIVACY:
    - Server-side role verification via require_admin dependency on every request.
    - Exposes only essential triaging user metadata (id, full_name, email). No password hashes or tokens.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT 
                sm.id, sm.user_id, sm.message, sm.sender, sm.status, sm.created_at,
                u.full_name as user_name, u.email as user_email
            FROM support_messages sm
            JOIN users u ON sm.user_id = u.id
            ORDER BY sm.created_at ASC, sm.id ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/admin/reply")
def create_admin_reply(
    payload: AdminReplyCreate,
    current_user: dict = Depends(require_admin)
):
    """
    Admin endpoint to reply to a user's support thread.
    SECURITY & PRIVACY:
    - Server-side role verification via require_admin.
    - Validates target user_id exists in users table before writing.
    - Parameterized query execution.
    """
    conn = get_connection()
    try:
        # Validate target user exists
        user_row = conn.execute(
            "SELECT id FROM users WHERE id = %s",
            (payload.user_id,)
        ).fetchone()

        if not user_row:
            raise HTTPException(status_code=404, detail="Target user conversation not found.")

        msg_text = payload.message.strip()
        if not msg_text:
            raise HTTPException(status_code=400, detail="Reply message cannot be empty.")

        cur = conn.execute(
            """
            INSERT INTO support_messages (user_id, message, sender, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, message, sender, status, created_at
            """,
            (payload.user_id, msg_text, "admin", "open")
        )
        conn.commit()
        row = cur.fetchone()
        return dict(row)
    finally:
        conn.close()


@router.patch("/admin/messages/{message_id}/status")
def update_message_status(
    message_id: int,
    payload: StatusUpdate,
    current_user: dict = Depends(require_admin)
):
    """
    Admin endpoint to update status of a support message or thread.
    """
    conn = get_connection()
    try:
        msg = conn.execute(
            "SELECT id, user_id FROM support_messages WHERE id = %s",
            (message_id,)
        ).fetchone()

        if not msg:
            raise HTTPException(status_code=404, detail="Support message not found.")

        # Update status for all messages in this user's thread to keep thread status in sync
        conn.execute(
            "UPDATE support_messages SET status = %s WHERE user_id = %s",
            (payload.status, msg["user_id"])
        )
        conn.commit()
        return {"status": "success", "message_id": message_id, "new_status": payload.status}
    finally:
        conn.close()


@router.patch("/admin/user/{target_user_id}/status")
def update_user_thread_status(
    target_user_id: int,
    payload: StatusUpdate,
    current_user: dict = Depends(require_admin)
):
    """
    Admin endpoint to update status of an entire conversation thread by user_id.
    """
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE support_messages SET status = %s WHERE user_id = %s",
            (payload.status, target_user_id)
        )
        conn.commit()
        return {"status": "success", "user_id": target_user_id, "new_status": payload.status}
    finally:
        conn.close()
