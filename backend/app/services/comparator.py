import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.nlp_service import get_policy_by_id
from app.services.fine_extractor import extract_fines
import app.services.recommender as recommender

# --- Keywords for Rubric ---
STRICT_KEYWORDS = {"must", "shall", "required", "mandatory", "penalty", "enforce", "prohibited", "liable", "fine", "obligation"}
GUIDANCE_KEYWORDS = {"should", "may", "recommend", "voluntary", "encourage", "guidance", "best practice", "principles", "flexible"}
RIGHTS_KEYWORDS = {"right to", "consent", "entitled", "opt-out", "transparency", "subject", "empower", "protect", "individual", "consumer"}
TECH_KEYWORDS = {"algorithm", "encryption", "audit", "cyber", "network", "system", "infrastructure", "data", "model", "parameter", "software", "api"}

def extract_sentences(text: str) -> list:
    # Basic regex sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out very short or empty strings
    return [s for s in sentences if len(s.split()) > 4]

def extract_clause_gaps(content1: str, content2: str, max_extracts: int = 3) -> dict:
    sents1 = extract_sentences(content1)
    sents2 = extract_sentences(content2)
    
    if not sents1 or not sents2:
        return {"orphaned_in_1": [], "orphaned_in_2": []}
        
    try:
        # Generate dense embeddings for all sentences
        emb1 = recommender._model.encode(sents1, show_progress_bar=False)
        emb2 = recommender._model.encode(sents2, show_progress_bar=False)
        
        # Matrix: N x M
        sim_matrix = cosine_similarity(emb1, emb2)
        
        # Find maximum similarity for each sentence in document 1 against document 2
        max_sim_1 = np.max(sim_matrix, axis=1)
        # Find maximum similarity for each sentence in document 2 against document 1
        max_sim_2 = np.max(sim_matrix, axis=0)
        
        # Sort by lowest maximum similarity (these are the orphans!)
        orphaned_1_idx = np.argsort(max_sim_1)
        orphaned_2_idx = np.argsort(max_sim_2)
        
        orphaned_in_1 = []
        for idx in orphaned_1_idx:
            if max_sim_1[idx] < 0.4:  # Threshold for being an orphan
                orphaned_in_1.append({"text": sents1[idx], "max_sim": float(max_sim_1[idx])})
                if len(orphaned_in_1) == max_extracts: break
                
        orphaned_in_2 = []
        for idx in orphaned_2_idx:
            if max_sim_2[idx] < 0.4:
                orphaned_in_2.append({"text": sents2[idx], "max_sim": float(max_sim_2[idx])})
                if len(orphaned_in_2) == max_extracts: break
                
        return {
            "orphaned_in_1": orphaned_in_1,
            "orphaned_in_2": orphaned_in_2
        }
    except Exception as e:
        print("Clause gap extraction failed:", e)
        return {"orphaned_in_1": [], "orphaned_in_2": []}

def calculate_rubric(content: str, has_fines: bool) -> dict:
    content_lower = content.lower()
    total_words = len(content_lower.split())
    if total_words == 0: total_words = 1
    
    strict_count = sum(len(re.findall(r'\b' + k + r'\b', content_lower)) for k in STRICT_KEYWORDS)
    rights_count = sum(len(re.findall(r'\b' + k + r'\b', content_lower)) for k in RIGHTS_KEYWORDS)
    tech_count   = sum(len(re.findall(r'\b' + k + r'\b', content_lower)) for k in TECH_KEYWORDS)
    
    # Calculate scores (0 to 100 normalized heuristically)
    # 1. Prescriptiveness (Binding Density)
    prescriptiveness = min(100, (strict_count / (total_words / 100)) * 25)
    
    # 2. Rights Orientation
    rights_orientation = min(100, (rights_count / (total_words / 100)) * 30)
    
    # 3. Technical Specificity
    technical_specificity = min(100, (tech_count / (total_words / 100)) * 15)
    
    # 4. Enforcement Power
    enforcement_power = 95.0 if has_fines else min(100, prescriptiveness * 0.5)
    
    return {
        "prescriptiveness": round(prescriptiveness),
        "rights_orientation": round(rights_orientation),
        "technical_specificity": round(technical_specificity),
        "enforcement_power": round(enforcement_power)
    }

def extract_core_themes(content1: str, content2: str) -> dict:
    if not content1 or not content2:
        return {"shared": [], "unique_1": [], "unique_2": []}
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_features=100)
        tfidf_matrix = vectorizer.fit_transform([content1, content2])
        feature_names = vectorizer.get_feature_names_out()
        
        arr = tfidf_matrix.toarray()
        doc1_scores = arr[0]
        doc2_scores = arr[1]
        
        shared, unique_1, unique_2 = [], [], []
        for i, word in enumerate(feature_names):
            s1, s2 = doc1_scores[i], doc2_scores[i]
            if s1 > 0.05 and s2 > 0.05:
                shared.append((word, s1 + s2))
            elif s1 > 0.1 and s2 < 0.02:
                unique_1.append((word, s1))
            elif s2 > 0.1 and s1 < 0.02:
                unique_2.append((word, s2))
                
        shared = [w for w, s in sorted(shared, key=lambda x: -x[1])][:5]
        unique_1 = [w for w, s in sorted(unique_1, key=lambda x: -x[1])][:5]
        unique_2 = [w for w, s in sorted(unique_2, key=lambda x: -x[1])][:5]
        
        return {"shared": shared, "unique_1": unique_1, "unique_2": unique_2}
    except Exception as e:
        print("TFIDF extraction failed:", e)
        return {"shared": [], "unique_1": [], "unique_2": []}


def compare_policies(id1: str, id2: str) -> dict:
    recommender._ensure_trained()
    
    p1 = get_policy_by_id(id1)
    p2 = get_policy_by_id(id2)
    if not p1 or not p2:
        return {"error": "One or both policies not found"}

    p1_cache = next((p for p in recommender._policy_data if p["id"] == id1), None)
    p2_cache = next((p for p in recommender._policy_data if p["id"] == id2), None)
    
    semantic_similarity = 0.0
    if p1_cache and p2_cache and p1_cache.get("embedding_idx") is not None and p2_cache.get("embedding_idx") is not None:
        emb1 = recommender._embeddings[p1_cache["embedding_idx"]].reshape(1, -1)
        emb2 = recommender._embeddings[p2_cache["embedding_idx"]].reshape(1, -1)
        semantic_similarity = max(0.0, float(cosine_similarity(emb1, emb2)[0][0]))
        
    themes = extract_core_themes(p1.get("content", ""), p2.get("content", ""))
    
    p1_fines = extract_fines(p1.get("content", "")) or {}
    p2_fines = extract_fines(p2.get("content", "")) or {}

    # Calculate Analyst Rubric
    rubric1 = calculate_rubric(p1.get("content", ""), bool(p1_fines.get("has_fines")))
    rubric2 = calculate_rubric(p2.get("content", ""), bool(p2_fines.get("has_fines")))
    
    # Calculate Clause-Level Gaps
    clause_gaps = extract_clause_gaps(p1.get("content", ""), p2.get("content", ""))

    return {
        "policy_1": {
            **{k: p1[k] for k in ["id", "title", "country", "sector", "region", "year", "tags", "status", "source_url"]},
            "penalty_fines": p1_fines,
            "rubric": rubric1
        },
        "policy_2": {
            **{k: p2[k] for k in ["id", "title", "country", "sector", "region", "year", "tags", "status", "source_url"]},
            "penalty_fines": p2_fines,
            "rubric": rubric2
        },
        "ml_metrics": {
            "semantic_similarity_score": semantic_similarity,
            "themes": themes,
            "clause_gaps": clause_gaps
        },
        "same_sector": p1["sector"] == p2["sector"]
    }