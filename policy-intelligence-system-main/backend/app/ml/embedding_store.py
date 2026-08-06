import sys
import numpy as np
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection


def _parse_db_vector(val) -> np.ndarray or None:
    """
    Helper function to parse DB vector column output into a numpy array.
    Handles None, lists, existing numpy arrays, and raw string formats
    like '[0.123,0.456,...]' from pgvector.
    """
    if val is None:
        return None
    if isinstance(val, np.ndarray):
        return val
    if isinstance(val, list):
        return np.array(val, dtype=np.float32)
    if isinstance(val, str):
        val = val.strip()
        if val.startswith('[') and val.endswith(']'):
            val = val[1:-1]
        if not val:
            return np.array([], dtype=np.float32)
        parts = [float(x) for x in val.split(',') if x.strip()]
        return np.array(parts, dtype=np.float32)
    return None


def store_embedding(policy_id: str, embedding: np.ndarray, model_name: str):
    """
    Updates the policies table for a specific policy.
    Sets embedding column (cast numpy to list for pgvector),
    embedding_model, and last_embedded_at to the current timestamp.
    """
    emb_list = embedding.tolist()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE policies
            SET embedding = %s::vector,
                embedding_model = %s,
                last_embedded_at = NOW()
            WHERE id = %s
            """,
            (emb_list, model_name, policy_id)
        )
        conn.commit()
    finally:
        conn.close()


def get_embedding(policy_id: str) -> np.ndarray or None:
    """
    Retrieves the embedding vector for a policy.
    Returns the vector as a numpy array or None if not found or not embedded.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT embedding FROM policies WHERE id = %s",
            (policy_id,)
        )
        row = cur.fetchone()
        if row and row[0] is not None:
            return _parse_db_vector(row[0])
    finally:
        conn.close()
    return None


def get_all_embeddings() -> list:
    """
    Returns all policies that have embeddings.
    Each dict contains: id, title, sector, country, region, embedding (as numpy array).
    Used for clustering or downstream analysis.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, embedding
            FROM policies
            WHERE embedding IS NOT NULL
            """
        )
        rows = cur.fetchall()
        results = []
        for row in rows:
            emb = _parse_db_vector(row['embedding'])
            if emb is not None:
                results.append({
                    "id": row['id'],
                    "title": row['title'],
                    "sector": row['sector'],
                    "country": row['country'],
                    "region": row['region'],
                    "embedding": emb
                })
        return results
    finally:
        conn.close()


def find_similar_by_vector(
    embedding: np.ndarray,
    n: int = 50,
    exclude_id: str = None,
    sector_filter: str = None
) -> list:
    """
    Uses the pgvector cosine distance operator (<=>) to find similar policies.
    Returns the top n most similar policies with calculated similarity scores.
    Excludes the source policy itself if exclude_id is provided.
    Filters by sector if sector_filter is provided.
    Each result contains: id, title, sector, country, region, similarity_score.
    """
    emb_list = embedding.tolist()

    query = """
        SELECT id, title, sector, country, region, (1 - (embedding <=> %s::vector)) as similarity_score
        FROM policies
        WHERE embedding IS NOT NULL
    """
    params = [emb_list]

    if exclude_id:
        query += " AND id != %s"
        params.append(exclude_id)

    if sector_filter:
        query += " AND sector = %s"
        params.append(sector_filter)

    query += " ORDER BY embedding <=> %s::vector ASC LIMIT %s"
    params.extend([emb_list, n])

    conn = get_connection()
    try:
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "title": row['title'],
                "sector": row['sector'],
                "country": row['country'],
                "region": row['region'],
                "similarity_score": float(row['similarity_score']) if row['similarity_score'] is not None else 0.0
            })
        return results
    finally:
        conn.close()


def batch_store_embeddings(policies: list):
    """
    Takes a list of policy dicts, generates an embedding for each using embed_policy(),
    and stores all updates in a single database transaction.
    Prints progress every 50 policies.
    """
    if not policies:
        print("[INFO] No policies provided for batch embedding.")
        return

    # Import dynamically to avoid circular dependencies
    from app.ml.embedder import embed_policy

    print(f"[INFO] Initializing batch embedding for {len(policies)} policies...")

    conn = get_connection()
    try:
        for idx, p in enumerate(policies, 1):
            policy_id = p.get("id")
            if not policy_id:
                print(f"[WARN] Policy at index {idx} has no ID. Skipping.")
                continue

            # Generate embedding
            emb = embed_policy(p)
            emb_list = emb.tolist()

            # Identify model dynamically based on vector dimension
            dim = len(emb_list)
            if dim == 768:
                model_name = "nlpaueb/legal-bert-base-uncased"
            elif dim == 384:
                model_name = "all-MiniLM-L6-v2"
            else:
                model_name = f"unknown-dimension-{dim}"

            # Execute update statement in the ongoing transaction
            conn.execute(
                """
                UPDATE policies
                SET embedding = %s::vector,
                    embedding_model = %s,
                    last_embedded_at = NOW()
                WHERE id = %s
                """,
                (emb_list, model_name, policy_id)
            )

            if idx % 50 == 0:
                print(f"[PROGRESS] Embedded and stored {idx}/{len(policies)} policies...")

        conn.commit()
        print(f"[SUCCESS] Bulk embedding transaction committed successfully. Total processed: {len(policies)}")
    except Exception as e:
        try:
            conn.conn.rollback()
            print("[INFO] Transaction rolled back due to error.")
        except Exception:
            pass
        print(f"[ERROR] Failed during batch embedding transaction: {e}")
        raise e
    finally:
        conn.close()
