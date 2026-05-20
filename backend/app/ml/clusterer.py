import sys
from pathlib import Path
import numpy as np
import umap
import hdbscan

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedding_store import get_all_embeddings

class PolicyClusterer:
    def __init__(self):
        # Initialize UMAP reducer
        self.reducer = umap.UMAP(
            n_components=50,
            n_neighbors=15,
            min_dist=0.1,
            metric="cosine",
            random_state=42
        )
        # Initialize HDBSCAN
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=5,
            min_samples=3,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True
        )
        self.fitted = False
        self.reduced_embeddings = None
        self.policy_ids = []
        self.labels_ = None
        self.probabilities_ = None

    def fit(self, embeddings: np.ndarray, policy_ids: list) -> dict:
        """
        Run UMAP to reduce dimensions, then run HDBSCAN on reduced embeddings.
        Store results internally.
        """
        if len(embeddings) == 0:
            print("[WARN] Empty embeddings passed to fit. Cannot cluster.")
            return {}

        self.policy_ids = list(policy_ids)
        print(f"[INFO] Fitting UMAP on {len(embeddings)} embeddings of dimension {embeddings.shape[1]}...")
        # 1. Reduce dimensions
        self.reduced_embeddings = self.reducer.fit_transform(embeddings)

        print("[INFO] Running HDBSCAN clustering on reduced embeddings...")
        # 2. Fit HDBSCAN
        self.clusterer.fit(self.reduced_embeddings)
        self.labels_ = self.clusterer.labels_
        self.probabilities_ = self.clusterer.probabilities_
        self.fitted = True

        # Calculate cluster statistics
        unique_labels = set(self.labels_)
        n_clusters = len(unique_labels - {-1})
        n_noise = list(self.labels_).count(-1)

        cluster_counts = {}
        for label in self.labels_:
            if label != -1:
                cluster_counts[label] = cluster_counts.get(label, 0) + 1

        largest_size = max(cluster_counts.values()) if cluster_counts else 0
        smallest_size = min(cluster_counts.values()) if cluster_counts else 0

        print("\n" + "=" * 50)
        print("CLUSTERING SUMMARY")
        print("=" * 50)
        print(f"Total policies:            {len(embeddings)}")
        print(f"Clusters found:            {n_clusters}")
        print(f"Noise points (unclustered): {n_noise}")
        if n_clusters > 0:
            print(f"Largest cluster size:      {largest_size}")
            print(f"Smallest cluster size:     {smallest_size}")
        print("=" * 50 + "\n")

        # Return dict of {policy_id: cluster_label}
        mapping = {}
        for p_id, label in zip(self.policy_ids, self.labels_):
            mapping[p_id] = int(label)

        return mapping

    def predict_single(self, embedding: np.ndarray) -> tuple:
        """
        For a NEW policy not in training set.
        Reduce with fitted UMAP, then use hdbscan.approximate_predict().
        Returns (cluster_id, confidence_score).
        """
        if not self.fitted:
            print("[WARN] Clusterer is not fitted yet. Returning (-1, 0.0)")
            return (-1, 0.0)

        try:
            # Reshape if single embedding is 1D
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)

            # Reduce with fitted UMAP
            reduced_emb = self.reducer.transform(embedding)

            # Use hdbscan.approximate_predict
            labels, strengths = hdbscan.approximate_predict(self.clusterer, reduced_emb)
            return int(labels[0]), float(strengths[0])
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return (-1, 0.0)

    def get_cluster_summary(self) -> dict:
        """
        Returns {cluster_id: [list of policy_ids]}.
        Excludes noise cluster (-1) as separate key "noise".
        """
        if not self.fitted:
            return {}

        summary = {"noise": []}
        for p_id, label in zip(self.policy_ids, self.labels_):
            label_int = int(label)
            if label_int == -1:
                summary["noise"].append(p_id)
            else:
                if label_int not in summary:
                    summary[label_int] = []
                summary[label_int].append(p_id)

        return summary


def run_clustering_job() -> dict:
    """
    Loads all embeddings, runs PolicyClusterer.fit(),
    updates database fields, and returns the cluster summary dict.
    """
    print("[INFO] Starting clustering job...")
    policies = get_all_embeddings()
    if not policies:
        print("[WARN] No embedded policies found in the database. Cannot run clustering job.")
        return {}

    embeddings = np.array([p["embedding"] for p in policies], dtype=np.float32)
    policy_ids = [p["id"] for p in policies]

    # Fit using our singleton instance
    mapping = _clusterer.fit(embeddings, policy_ids)
    
    # Expose probabilities for confidence updates
    probabilities = _clusterer.probabilities_

    print("Saving cluster labels to database...")
    conn = get_connection()
    try:
        # Perform updates in a single transaction
        for idx, (p_id, label) in enumerate(mapping.items()):
            prob = float(probabilities[idx]) if probabilities is not None else 1.0
            conn.execute(
                """
                UPDATE policies
                SET cluster_id = %s,
                    cluster_confidence = %s
                WHERE id = %s
                """,
                (label, prob, p_id)
            )
        conn.commit()
        print(f"[SUCCESS] Updated {len(mapping)} policies with cluster labels and confidences.")
    except Exception as e:
        print(f"[ERROR] Failed to save cluster results to database: {e}")
        try:
            conn.conn.rollback()
        except Exception:
            pass
        raise e
    finally:
        conn.close()

    summary = _clusterer.get_cluster_summary()
    return summary


# Module-level singleton
_clusterer = PolicyClusterer()


if __name__ == "__main__":
    summary = run_clustering_job()
    print("\n--- Full Cluster Summary (Policy IDs per Cluster) ---")
    for cid, p_list in summary.items():
        if cid == "noise":
            print(f"Noise (Unclustered): {len(p_list)} policies")
        else:
            print(f"Cluster #{cid}: {len(p_list)} policies")
