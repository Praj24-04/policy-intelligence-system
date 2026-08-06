import re
import sys
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

# =====================================================================
# 1. Module-Level Model Loading with Fail-Safe Fallbacks
# =====================================================================

bi_encoder = None
cross_encoder = None
LOADED_MODEL_NAME = ""

# Attempt to load Bi-Encoder
try:
    print("[INFO] Attempting to load primary Bi-Encoder: 'nlpaueb/legal-bert-base-uncased'...")
    bi_encoder = SentenceTransformer("nlpaueb/legal-bert-base-uncased")
    LOADED_MODEL_NAME = "nlpaueb/legal-bert-base-uncased"
    print("[SUCCESS] Primary Bi-Encoder 'nlpaueb/legal-bert-base-uncased' loaded successfully.")
except Exception as e:
    print(f"[WARN] Failed to load primary Bi-Encoder: {e}")
    try:
        print("[INFO] Attempting to load fallback Bi-Encoder: 'all-mpnet-base-v2'...")
        bi_encoder = SentenceTransformer("all-mpnet-base-v2")
        LOADED_MODEL_NAME = "all-mpnet-base-v2"
        print("[SUCCESS] Fallback Bi-Encoder 'all-mpnet-base-v2' loaded successfully.")
    except Exception as ex:
        print(f"[ERROR] Failed to load fallback Bi-Encoder: {ex}")
        try:
            print("[INFO] Attempting to load emergency Bi-Encoder: 'all-MiniLM-L6-v2'...")
            bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
            LOADED_MODEL_NAME = "all-MiniLM-L6-v2"
            print("[SUCCESS] Emergency Bi-Encoder 'all-MiniLM-L6-v2' loaded successfully.")
        except Exception as err:
            print(f"[CRITICAL] All Bi-Encoder loads failed: {err}")
            raise err

# Attempt to load Cross-Encoder for Reranking
try:
    print("[INFO] Attempting to load Cross-Encoder: 'cross-encoder/ms-marco-MiniLM-L-6-v2'...")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    print("[SUCCESS] Cross-Encoder loaded successfully.")
except Exception as e:
    print(f"[WARN] Failed to load Cross-Encoder: {e}. Reranking will use fallback scores.")
    cross_encoder = None


# =====================================================================
# 2. Smart Chunking Helper
# =====================================================================

def _smart_chunk(text: str, size: int = 256) -> list:
    """
    Split text on sentence boundaries and group into chunks up to size words.
    Overlaps chunks by making the last sentence of the previous chunk the
    first sentence of the next chunk. Chunks under 20 words are discarded.
    """
    if not text:
        return []
        
    # Split using sentence boundaries (. ! ?) while keeping the punctuation
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_words = 0

    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        # If adding this sentence exceeds size limit and we have elements in current chunk
        if current_words + sentence_words > size and current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.split()) >= 20:
                chunks.append(chunk_text)
            
            # Slide window: last sentence overlapping
            overlap_sentence = current_chunk[-1]
            current_chunk = [overlap_sentence, sentence]
            current_words = len(overlap_sentence.split()) + sentence_words
        else:
            current_chunk.append(sentence)
            current_words += sentence_words

    # Append remaining sentences
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        if len(chunk_text.split()) >= 20:
            chunks.append(chunk_text)

    return chunks


# =====================================================================
# 3. Weighted Policy Embedding
# =====================================================================

def embed_policy(policy: dict) -> np.ndarray:
    """
    Computes a weighted mean representation of a policy across its fields:
    - Title: Weight 4.0
    - Tags: Weight 3.0
    - Sector/Country Meta: Weight 2.0
    - Content Chunks (max 6): Weight 1.0 each
    Batch encodes all texts in a single call.
    Returns (D,) shape numpy array.
    """
    texts = []
    weights = []

    # 1. Title (Weight 4.0)
    title = policy.get("title", "") or ""
    texts.append(title)
    weights.append(4.0)

    # 2. Tags (Weight 3.0)
    tags = policy.get("tags")
    if isinstance(tags, list):
        tags_str = " ".join(tags)
    elif isinstance(tags, str):
        tags_str = tags
    else:
        tags_str = ""
    texts.append(tags_str)
    weights.append(3.0)

    # 3. Sector & Country Metadata (Weight 2.0)
    sector = policy.get("sector", "") or ""
    country = policy.get("country", "") or ""
    meta_str = f"{sector} policy in {country}"
    texts.append(meta_str)
    weights.append(2.0)

    # 4. Content chunks (Max 6, Weight 1.0 each)
    content = policy.get("content", "") or ""
    chunks = _smart_chunk(content)
    selected_chunks = chunks[:6]

    for chunk in selected_chunks:
        texts.append(chunk)
        weights.append(1.0)

    # Batch encode all components in a single bi-encoder call
    embeddings = bi_encoder.encode(texts)  # Shape: (N, D)

    # Calculate weighted mean
    weights_arr = np.array(weights).reshape(-1, 1)  # Shape: (N, 1)
    weighted_sum = np.sum(embeddings * weights_arr, axis=0)
    sum_weights = np.sum(weights)

    weighted_mean = weighted_sum / (sum_weights if sum_weights > 0 else 1.0)
    return weighted_mean


# =====================================================================
# 4. Text Embedding (Single query / Need gap match)
# =====================================================================

def embed_text(text: str) -> np.ndarray:
    """
    Returns single vector embedding for search queries or need gap texts.
    No weighting applied. Shape: (D,)
    """
    embeddings = bi_encoder.encode([text])
    return embeddings[0]


# =====================================================================
# 5. Cross-Encoder Reranking
# =====================================================================

def rerank_with_cross_encoder(query_text: str, candidates: list) -> list:
    """
    Reranks candidates based on the Cross-Encoder model.
    Each candidate must be a dict containing a 'content' key.
    Pairs (query, candidate content up to 512 chars) are passed.
    Adds a 'rerank_score' to each candidate and returns sorted list.
    """
    if not candidates:
        return []

    # Safe fallback if cross-encoder loading failed
    if cross_encoder is None:
        for candidate in candidates:
            candidate["rerank_score"] = 0.0
        return candidates

    try:
        pairs = []
        for candidate in candidates:
            content = candidate.get("content", "") or ""
            pairs.append((query_text, content[:512]))

        # Predict scores in a single batch
        scores = cross_encoder.predict(pairs)

        # Assign score
        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        # Sort descending by rerank score
        return sorted(candidates, key=lambda x: -x["rerank_score"])
    except Exception as e:
        print(f"[WARN] Error during Cross-Encoder reranking: {e}. Returning unranked candidates.")
        for candidate in candidates:
            candidate["rerank_score"] = 0.0
        return candidates


# =====================================================================
# 6. Get Embedding Dimension Check
# =====================================================================

def get_embedding_dimension() -> int:
    """
    Checks the dimension of the loaded Bi-Encoder.
    Returns 768 for Legal-BERT / MPNet, or 384 for MiniLM.
    """
    test_emb = embed_text("dimension check")
    return int(test_emb.shape[0])


# =====================================================================
# 7. Test Suite
# =====================================================================

if __name__ == "__main__":
    print("\n--- Running Pre-Flight Tests for backend/app/ml/embedder.py ---")
    
    # 1. Fake Policy Embedding
    fake_policy = {
        "title": "AI Transparency Act 2026",
        "tags": ["AI", "Transparency", "Safety"],
        "sector": "AI Governance",
        "country": "United States",
        "content": "This act establishes baseline transparency protocols for artificial intelligence. "
                   "Developers must disclose large-scale dataset training models. "
                   "Independent audits are required to verify security parameters and avoid downstream bias."
    }
    
    print("\nTesting: embed_policy()")
    policy_vector = embed_policy(fake_policy)
    print(f"  Result Vector Shape: {policy_vector.shape}")
    print(f"  Result Vector Type:  {type(policy_vector)}")
    print(f"  First 5 Vector Values: {policy_vector[:5]}")
    
    # 2. Single Text Embedding
    print("\nTesting: embed_text()")
    text_vector = embed_text("data privacy regulation")
    print(f"  Result Vector Shape: {text_vector.shape}")
    
    # 3. Cross-Encoder Reranking
    fake_candidates = [
        {"id": 1, "content": "General regulations regarding software development lifecycle and API versioning."},
        {"id": 2, "content": "Data privacy regulation and protection strategies including encryption at rest."}
    ]
    
    print("\nTesting: rerank_with_cross_encoder()")
    ranked = rerank_with_cross_encoder("data privacy regulation", fake_candidates)
    
    for rank, candidate in enumerate(ranked, 1):
        print(f"  Rank {rank}: Candidate ID {candidate['id']} | Score: {candidate['rerank_score']:.4f} | Preview: '{candidate['content'][:40]}...'")
    
    print("\nEmbedding Dimension: ", get_embedding_dimension())
    print("\n--- Pre-Flight Tests Completed ---")
