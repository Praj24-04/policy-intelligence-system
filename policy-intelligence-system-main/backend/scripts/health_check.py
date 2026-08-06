import sys
import traceback
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection


def check_postgres() -> bool:
    print("[RUNNING] Check 1: PostgreSQL Connection...", end="", flush=True)
    try:
        conn = get_connection()
        cur = conn.execute("SELECT 1 as alive")
        row = cur.fetchone()
        conn.close()
        if row and row["alive"] == 1:
            print(" PASS")
            return True
        else:
            print(" FAIL (Unexpected returned row)")
            return False
    except Exception as e:
        print(f" FAIL\n  Details: {e}")
        return False


def check_pgvector() -> bool:
    print("[RUNNING] Check 2: pgvector Extension Status...", end="", flush=True)
    try:
        conn = get_connection()
        cur = conn.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        conn.close()
        if row and row["extname"] == "vector":
            print(" PASS")
            return True
        else:
            print(" FAIL (pgvector extension is not registered or active in PostgreSQL)")
            return False
    except Exception as e:
        print(f" FAIL\n  Details: {e}")
        return False


def check_chromadb() -> bool:
    print("[RUNNING] Check 3: ChromaDB Collection Status...", end="", flush=True)
    try:
        from app.ml.vector_store import client
        collection = client.get_collection(name="policies_v2")
        count = collection.count()
        if count >= 0:
            print(f" PASS (Found 'policies_v2' collection with {count} items indexed)")
            return True
        else:
            print(" FAIL (Invalid collection count returned)")
            return False
    except Exception as e:
        print(f" FAIL\n  Details: {e}")
        return False


def check_embedding_model() -> bool:
    print("[RUNNING] Check 4: Embedding Model Loading...", end="", flush=True)
    try:
        from app.ml.embedder import bi_encoder, get_embedding_dimension, LOADED_MODEL_NAME
        if bi_encoder is None:
            raise ValueError("Bi-Encoder instance is None")
        dim = get_embedding_dimension()
        print(f" PASS (Loaded '{LOADED_MODEL_NAME}' successfully with dimension {dim})")
        return True
    except Exception as e:
        print(f" FAIL\n  Details: {e}")
        return False


def check_sample_recommendation() -> bool:
    print("[RUNNING] Check 5: Recommender V2 End-to-End Test...", end="", flush=True)
    try:
        from app.ml.recommender_v2 import get_recommendations_v2
        conn = get_connection()
        # Retrieve a policy with embeddings active to run recommender test
        cur = conn.execute("SELECT id FROM policies WHERE embedding IS NOT NULL LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if not row:
            print(" FAIL (No policies with active embeddings found in database to test with)")
            return False

        policy_id = row["id"]
        results = get_recommendations_v2(policy_id, top_n=2)

        if "error" in results:
            print(f" FAIL (Recommender returned error: {results['error']})")
            return False

        if not results.get("recommendations"):
            print(" FAIL (Returned recommendation array is empty)")
            return False

        print(" PASS")
        return True
    except Exception as e:
        print(" FAIL")
        traceback.print_exc(file=sys.stdout)
        return False


def check_sample_comparison() -> bool:
    print("[RUNNING] Check 6: Comparator V2 End-to-End Test...", end="", flush=True)
    try:
        from app.ml.comparator_v2 import compare_policies_v2
        conn = get_connection()
        # Retrieve two policies with embeddings active to run comparator test
        cur = conn.execute("SELECT id FROM policies WHERE embedding IS NOT NULL LIMIT 2")
        rows = cur.fetchall()
        conn.close()

        if len(rows) < 2:
            print(" FAIL (Need at least 2 policies with embeddings active in database to run comparison test)")
            return False

        id1 = rows[0]["id"]
        id2 = rows[1]["id"]

        results = compare_policies_v2(id1, id2)

        if "error" in results:
            print(f" FAIL (Comparator returned error: {results['error']})")
            return False

        if "overall_metrics" not in results:
            print(" FAIL (overall_metrics key missing from comparator output)")
            return False

        print(" PASS")
        return True
    except Exception as e:
        print(" FAIL")
        traceback.print_exc(file=sys.stdout)
        return False


def main():
    print("=" * 70)
    print("                POLICYIQ PRE-DEPLOYMENT SYSTEM HEALTH CHECK")
    print("=" * 70)

    checks = [
        check_postgres,
        check_pgvector,
        check_chromadb,
        check_embedding_model,
        check_sample_recommendation,
        check_sample_comparison,
    ]

    all_passed = True
    for check_func in checks:
        success = check_func()
        if not success:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("  [OK] SYSTEM STATUS: ALL CHECKS PASSED. DEPLOYMENT READY!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("  [FAIL] SYSTEM STATUS: FAILURES DETECTED. DO NOT DEPLOY!")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
