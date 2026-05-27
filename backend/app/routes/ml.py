import os
import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth import get_current_user
from app.database import get_connection
from app.ml.embedder import LOADED_MODEL_NAME
from app.ml.vector_store import collection
from app.ml.scheduler import embed_new_policies
from app.limiter import limiter

router = APIRouter()


def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required.")
    return current_user


@router.get("/status")
def get_ml_status():
    _backend_root = Path(__file__).parent.parent.parent
    chroma_path = _backend_root / "data" / "chroma_db"

    # 1. Last retrain timestamp
    if chroma_path.exists():
        last_retrain = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(os.path.getmtime(chroma_path)))
    else:
        last_retrain = "Never"

    # 2. Chroma count
    chroma_count = collection.count() if collection is not None else 0

    # 3. Database counts
    conn = get_connection()
    try:
        total_p = conn.execute("SELECT count(*) as cnt FROM policies").fetchone()["cnt"]
        embedded_p = conn.execute("SELECT count(*) as cnt FROM policies WHERE embedding IS NOT NULL").fetchone()["cnt"]
        cluster_cnt = conn.execute("SELECT count(distinct cluster_id) as cnt FROM policies WHERE cluster_id IS NOT NULL AND cluster_id != -1").fetchone()["cnt"]
    except Exception as e:
        print(f"[ERROR] Failed to query ML status metrics: {e}")
        total_p = 0
        embedded_p = 0
        cluster_cnt = 0
    finally:
        conn.close()

    return {
        "total_policies": total_p,
        "total_embedded": embedded_p,
        "total_indexed_in_chroma": chroma_count,
        "cluster_count": cluster_cnt,
        "last_retrain_timestamp": last_retrain,
        "embedding_model_name": LOADED_MODEL_NAME or "nlpaueb/legal-bert-base-uncased"
    }


@router.post("/trigger-embed")
@limiter.limit("2/minute")
async def trigger_embed(request: Request, admin_user: dict = Depends(get_admin_user)):
    # Find count of unembedded policies before triggering
    conn = get_connection()
    try:
        before = conn.execute("SELECT count(*) as cnt FROM policies WHERE embedding IS NULL").fetchone()["cnt"]
    finally:
        conn.close()

    if before == 0:
        return {
            "message": "No new policies to embed.",
            "policies_embedded": 0
        }

    # Trigger embed_new_policies()
    try:
        await embed_new_policies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run embedding process: {str(e)}")

    # Check after
    conn = get_connection()
    try:
        after = conn.execute("SELECT count(*) as cnt FROM policies WHERE embedding IS NULL").fetchone()["cnt"]
    finally:
        conn.close()

    embedded_cnt = max(0, before - after)
    return {
        "message": f"Successfully triggered embedding. Embedded {embedded_cnt} policies.",
        "policies_embedded": embedded_cnt
    }
