from fastapi import APIRouter
from pydantic import BaseModel
from app.database import get_connection

router = APIRouter()

class FeedbackIn(BaseModel):
    policy_id: str
    country: str
    helpful: bool
    comment: str = ""

@router.post("/")
def submit_feedback(feedback: FeedbackIn):
    conn = get_connection()
    
    # Check if feedback already exists for this policy+country
    existing = conn.execute(
        "SELECT id FROM feedback WHERE policy_id = ? AND country = ?",
        (feedback.policy_id, feedback.country)
    ).fetchone()
    
    if existing:
        # Update existing feedback
        conn.execute(
            "UPDATE feedback SET helpful = ?, comment = ?, timestamp = CURRENT_TIMESTAMP WHERE policy_id = ? AND country = ?",
            (int(feedback.helpful), feedback.comment, feedback.policy_id, feedback.country)
        )
    else:
        # Insert new feedback
        conn.execute(
            "INSERT INTO feedback (policy_id, country, helpful, comment) VALUES (?,?,?,?)",
            (feedback.policy_id, feedback.country, int(feedback.helpful), feedback.comment)
        )
    
    conn.commit()
    conn.close()
    return {"status": "recorded", "helpful": feedback.helpful}

@router.get("/stats")
def feedback_stats():
    conn = get_connection()
    rows = conn.execute("""
        SELECT 
            policy_id,
            country,
            SUM(helpful) as positive,
            COUNT(*) - SUM(helpful) as negative,
            COUNT(*) as total
        FROM feedback
        GROUP BY policy_id, country
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/policy/{policy_id}")
def policy_feedback(policy_id: str):
    """Get all feedback for a specific policy."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT country, helpful, comment, timestamp
        FROM feedback
        WHERE policy_id = ?
        ORDER BY timestamp DESC
    """, (policy_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/summary")
def feedback_summary():
    """Overall feedback statistics."""
    conn = get_connection()
    
    total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    positive = conn.execute("SELECT COUNT(*) FROM feedback WHERE helpful = 1").fetchone()[0]
    negative = conn.execute("SELECT COUNT(*) FROM feedback WHERE helpful = 0").fetchone()[0]
    
    # Most helpful recommendations
    top_helpful = conn.execute("""
        SELECT policy_id, country, COUNT(*) as votes
        FROM feedback WHERE helpful = 1
        GROUP BY policy_id, country
        ORDER BY votes DESC LIMIT 5
    """).fetchall()
    
    # Most rejected recommendations  
    top_rejected = conn.execute("""
        SELECT policy_id, country, COUNT(*) as votes
        FROM feedback WHERE helpful = 0
        GROUP BY policy_id, country
        ORDER BY votes DESC LIMIT 5
    """).fetchall()
    
    conn.close()
    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "accuracy_rate": round(positive / total * 100, 1) if total > 0 else 0,
        "top_helpful": [dict(r) for r in top_helpful],
        "top_rejected": [dict(r) for r in top_rejected]
    }