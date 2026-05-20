import sys
import time
import json
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedder import embed_policy
from app.ml.embedding_store import store_embedding


def main():
    # 1. Fetch policies with NULL embedding
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, tags
            FROM policies
            WHERE embedding IS NULL
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    policies = []
    for r in rows:
        p = dict(r)
        # Parse tags safely
        if p.get("tags"):
            try:
                p["tags"] = json.loads(p["tags"]) if p["tags"].startswith("[") else [t.strip() for t in p["tags"].split(",") if t.strip()]
            except Exception:
                p["tags"] = [t.strip() for t in p.get("tags", "").split(",") if t.strip()]
        else:
            p["tags"] = []
        policies.append(p)

    total_policies = len(policies)
    if total_policies == 0:
        print("[INFO] No policies without embeddings found in the database. Nothing to do!")
        return

    # 5. Confirmation Prompt (auto-confirmed for automated execution)
    print(f"This will embed {total_policies} policies using Legal-BERT.")
    print("Auto-confirming embedding process...")
    confirm = 'y'
    if confirm.strip().lower() != 'y':
        print("[INFO] Embedding process canceled by the user.")
        return

    print(f"\n[INFO] Starting embedding process for {total_policies} policies...")
    start_time = time.time()

    embedded_count = 0
    failed_count = 0

    for idx, p in enumerate(policies, 1):
        title = p.get("title", "Untitled")
        policy_id = p.get("id")

        try:
            # Generate embedding using primary bi-encoder
            embedding = embed_policy(p)

            # Determine loaded model name
            from app.ml.embedder import LOADED_MODEL_NAME
            model_name = LOADED_MODEL_NAME

            # Store the embedding
            store_embedding(policy_id, embedding, model_name)

            embedded_count += 1
            print(f"Embedded {idx}/{total_policies}: '{title}'")

        except Exception as e:
            failed_count += 1
            print(f"[ERROR] Failed to embed policy ID {policy_id} ('{title}'): {e}")

        # Sleep for 0.5 seconds between batches of 20 to avoid memory pressure
        if idx % 20 == 0 and idx < total_policies:
            print("[INFO] Batch completed. Sleeping 0.5s to relieve memory pressure...")
            time.sleep(0.5)

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("EMBEDDING MIGRATION COMPLETED")
    print("=" * 60)
    print(f"Total policies processed: {total_policies}")
    print(f"Successfully embedded:   {embedded_count}")
    print(f"Failed to embed:         {failed_count}")
    print(f"Total time taken:        {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print("=" * 60)


if __name__ == "__main__":
    main()
