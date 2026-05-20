import sys
import random
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedding_store import get_all_embeddings, find_similar_by_vector


def main():
    # 1. Count policies with embeddings vs total
    conn = get_connection()
    try:
        cur_total = conn.execute("SELECT COUNT(*) as cnt FROM policies")
        total_count = cur_total.fetchone()['cnt']

        cur_embedded = conn.execute("SELECT COUNT(*) as cnt FROM policies WHERE embedding IS NOT NULL")
        embedded_count = cur_embedded.fetchone()['cnt']
    finally:
        conn.close()

    print("=" * 60)
    print("EMBEDDING STORAGE METRICS")
    print("=" * 60)
    print(f"Total policies in database:  {total_count}")
    print(f"Policies with embeddings:    {embedded_count}")

    if total_count > 0:
        pct = (embedded_count / total_count) * 100
        print(f"Embedding coverage:          {pct:.1f}%")
    print("=" * 60 + "\n")

    if embedded_count == 0:
        print("[WARN] No policies have embeddings yet. Run embed_all_policies.py first.")
        return

    # 2. Get all embedded policies to select random ones
    all_embedded = get_all_embeddings()
    if not all_embedded:
        print("[WARN] No embedded policies could be loaded.")
        return

    # Take up to 3 random policies
    sample_size = min(3, len(all_embedded))
    random_samples = random.sample(all_embedded, sample_size)

    print(f"Evaluating similarity quality for {sample_size} random sample policies:\n")

    # 3. Find top 5 similar policies for each sample
    for idx, sample in enumerate(random_samples, 1):
        print(f"Sample #{idx}:")
        print(f"  Title:   '{sample['title']}'")
        print(f"  ID:      {sample['id']}")
        print(f"  Sector:  {sample['sector']}")
        print(f"  Country: {sample['country']} ({sample['region']})")
        print("  " + "-" * 50)
        print("  Top 5 Semantically Similar Policies (Cosine Similarity):")

        # Call find_similar_by_vector with the sample's embedding
        similar_policies = find_similar_by_vector(
            embedding=sample['embedding'],
            n=5,
            exclude_id=sample['id']
        )

        if not similar_policies:
            print("    No similar policies found.")
        else:
            for rank, sim_p in enumerate(similar_policies, 1):
                score = sim_p['similarity_score']
                print(f"    Rank {rank}: [Score {score:.4f}] '{sim_p['title']}'")
                print(f"            Sector: {sim_p['sector']} | Country: {sim_p['country']} ({sim_p['region']})")
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
