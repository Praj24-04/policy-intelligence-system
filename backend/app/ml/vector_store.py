import sys
import numpy as np
import chromadb
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedding_store import get_embedding

# 1. Initialize ChromaDB PersistentClient
chroma_path = _backend_root / "data" / "chroma_db"
chroma_path.parent.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(chroma_path))

# 2. Get or create collection "policies_v2" with metadata hnsw:space set to cosine
try:
    collection = client.get_or_create_collection(
        name="policies_v2",
        metadata={"hnsw:space": "cosine"}
    )
except Exception as e:
    print(f"[ERROR] Failed to initialize policies_v2 collection on module load: {e}")
    collection = None


def _parse_db_vector(val) -> np.ndarray or None:
    """Helper to parse raw DB vector column to a numpy array."""
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


# 3. Function to sync one policy to ChromaDB
def sync_policy_to_chroma(policy: dict, embedding: np.ndarray):
    """Upserts one policy to the ChromaDB policies_v2 collection."""
    if collection is None:
        print("[WARN] Chroma collection is not initialized. Skipping upsert.")
        return

    policy_id = str(policy.get("id"))
    content = str(policy.get("content") or "")
    # Use first 1500 chars as the document representation
    document_snippet = content[:1500]

    metadata = {
        "title": str(policy.get("title") or ""),
        "sector": str(policy.get("sector") or ""),
        "country": str(policy.get("country") or ""),
        "region": str(policy.get("region") or ""),
        "year": str(policy.get("year")) if policy.get("year") is not None else "",
        "status": str(policy.get("status") or "Active"),
        "cluster_id": str(policy.get("cluster_id")) if policy.get("cluster_id") is not None else ""
    }

    collection.upsert(
        ids=[policy_id],
        embeddings=[embedding.tolist()],
        documents=[document_snippet],
        metadatas=[metadata]
    )


# 4. Function to sync all policies from PostgreSQL to ChromaDB
def sync_all_to_chroma():
    """Loads all policies with embeddings from PostgreSQL and upserts them to ChromaDB."""
    if collection is None:
        print("[WARN] Chroma collection is not initialized. Cannot perform sync.")
        return

    print("[INFO] Fetching all embedded policies from PostgreSQL...")
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, year, status, cluster_id, embedding
            FROM policies
            WHERE embedding IS NOT NULL
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    total_policies = len(rows)
    print(f"[INFO] Syncing {total_policies} policies to ChromaDB...")

    synced_count = 0
    for r in rows:
        p = dict(r)
        embedding_val = _parse_db_vector(p["embedding"])
        if embedding_val is None:
            continue

        sync_policy_to_chroma(p, embedding_val)
        synced_count += 1

        if synced_count % 100 == 0:
            print(f"[PROGRESS] Synced {synced_count}/{total_policies} policies to ChromaDB...")

    print(f"[SUCCESS] ChromaDB sync complete. Total synced: {synced_count} policies.")


# 5. Function to query ChromaDB for similar policies
def search_similar_chroma(
    policy_id: str,
    n: int = 50,
    sector_filter: str = None,
    exclude_same_country: bool = False
) -> list:
    """Queries ChromaDB to find similar policies using the source embedding from pgvector."""
    if collection is None:
        print("[WARN] Chroma collection is not initialized. Returning empty results.")
        return []

    # Retrieve embedding from pgvector
    embedding = get_embedding(policy_id)
    if embedding is None:
        print(f"[WARN] Policy embedding not found for policy ID: {policy_id}")
        return []

    # Get metadata of source policy to build filtering logic
    conn = get_connection()
    try:
        cur = conn.execute("SELECT country FROM policies WHERE id = %s", (policy_id,))
        row = cur.fetchone()
        source_country = row["country"] if row else None
    finally:
        conn.close()

    # Build filters (ChromaDB query syntax)
    conditions = []
    if sector_filter:
        conditions.append({"sector": {"$eq": sector_filter}})
    if exclude_same_country and source_country:
        conditions.append({"country": {"$ne": source_country}})

    where_filter = None
    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}

    # Query with slightly larger count to account for filtering the source policy out
    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=n + 5,
        where=where_filter
    )

    matches = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]

    for idx, match_id in enumerate(ids):
        # Remove the source policy itself from the results
        if match_id == policy_id:
            continue

        meta = metadatas[idx]
        dist = distances[idx]
        doc = documents[idx]

        # Convert cosine distance to approximate similarity score
        approx_similarity = 1.0 - float(dist)

        matches.append({
            "id": match_id,
            "title": meta.get("title", ""),
            "sector": meta.get("sector", ""),
            "country": meta.get("country", ""),
            "region": meta.get("region", ""),
            "content": doc,
            "approx_similarity": approx_similarity
        })

        if len(matches) >= n:
            break

    return matches


# 6. Function to drop and recreate ChromaDB collection
def rebuild_chroma_index():
    """Drops the policies_v2 collection, recreates it, and performs a fresh sync."""
    global collection
    if collection is None:
        print("[WARN] Collection was not active. Attempting fresh build...")

    print("[INFO] Rebuilding ChromaDB policies_v2 collection...")
    try:
        client.delete_collection("policies_v2")
    except Exception:
        pass

    collection = client.create_collection(
        name="policies_v2",
        metadata={"hnsw:space": "cosine"}
    )
    sync_all_to_chroma()


if __name__ == "__main__":
    print("[INFO] Rebuilding/syncing ChromaDB collection...")
    rebuild_chroma_index()

    # Get a sample policy ID from the database to run a test search
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, title FROM policies WHERE embedding IS NOT NULL LIMIT 1")
        row = cur.fetchone()
        sample_id = row["id"] if row else None
        sample_title = row["title"] if row else None
    finally:
        conn.close()

    if sample_id:
        print(f"\n[INFO] Running test search for sample policy: '{sample_title}' ({sample_id})")
        results = search_similar_chroma(sample_id, n=3)
        print(f"Found {len(results)} matches:")
        for idx, match in enumerate(results, 1):
            print(f"  Match #{idx}: [Approx Similarity: {match['approx_similarity']:.4f}] '{match['title']}' ({match['id']})")
            print(f"           Sector: {match['sector']} | Country: {match['country']}")
    else:
        print("[WARN] No embedded policies found in database to run a test search.")
