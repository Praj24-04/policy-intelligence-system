import sys
import json
import math
import logging
import numpy as np
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedder import embed_text, cross_encoder
from app.ml.embedding_store import get_embedding


def _parse_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _infer_approach(tags: list, title: str, sector: str) -> str:
    """Infers regulatory approach from tags, title, and sector."""
    tags_lower = [t.lower() for t in tags]
    text_context = " ".join(tags_lower) + " " + title.lower()

    if any(w in text_context for w in ["sandbox", "innovation", "voluntary", "soft-law", "flexible"]):
        return "Innovation-focused"
    elif any(w in text_context for w in ["risk", "assessment", "mitigation", "framework"]):
        return "Risk-based"
    elif any(w in text_context for w in ["fines", "penalties", "sanctions", "compliance", "mandatory", "audit"]):
        return "Compliance-driven"
    elif any(w in text_context for w in ["principles", "rights", "ethics", "transparency", "explainability"]):
        return "Principles-based"
    elif any(w in text_context for w in ["safety", "incident", "breach", "reporting", "threat", "resilience"]):
        return "Safety-first"
    else:
        # Sector based defaults
        if sector == "AI Governance":
            return "Principles-based"
        elif sector == "Cybersecurity":
            return "Safety-first"
        else:
            return "Compliance-driven"


# 1. New Upgrade Comparator Function
def compare_policies_v2(id1: str, id2: str) -> dict:
    # Part A - Retrieve both policies from PostgreSQL
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, tags, year, status 
            FROM policies 
            WHERE id IN (%s, %s)
            """,
            (id1, id2)
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    p1 = None
    p2 = None
    for r in rows:
        if r["id"] == id1:
            p1 = dict(r)
        if r["id"] == id2:
            p2 = dict(r)

    # Self-comparison fallback
    if id1 == id2 and p1:
        p2 = p1.copy()

    if not p1 or not p2:
        return {"error": f"One or both policies not found in database: '{id1}', '{id2}'"}

    p1["tags"] = _parse_list(p1.get("tags"))
    p2["tags"] = _parse_list(p2.get("tags"))

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Retrieve embeddings from pgvector
    emb1 = get_embedding(id1)
    emb2 = get_embedding(id2)

    # If either embedding is missing, embed on-the-fly
    if emb1 is None:
        try:
            from app.ml.embedder import embed_policy
            logger.warning(f"Embedding for policy {id1} is missing in pgvector. Embedding on-the-fly...")
            emb1 = embed_policy(p1)
        except Exception as e:
            logger.error(f"On-the-fly embedding failed for policy {id1}: {e}")

    if emb2 is None:
        try:
            from app.ml.embedder import embed_policy
            logger.warning(f"Embedding for policy {id2} is missing in pgvector. Embedding on-the-fly...")
            emb2 = embed_policy(p2)
        except Exception as e:
            logger.error(f"On-the-fly embedding failed for policy {id2}: {e}")

    if emb1 is None or emb2 is None:
        return {"error": "Embeddings not found and on-the-fly embedding failed for one or both policies"}

    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)

    # Part B - Overall semantic similarity (Cosine)
    dot_sem = np.dot(emb1, emb2)
    semantic_similarity = float(dot_sem / (norm1 * norm2)) if (norm1 > 0 and norm2 > 0) else 0.0
    semantic_similarity = max(0.0, min(1.0, semantic_similarity))

    # Part C - 6-Dimensional regulatory analysis
    anchors = {
        "enforcement": "penalties fines sanctions enforcement liability",
        "scope": "applicability jurisdiction coverage applies to",
        "rights": "citizen rights individual rights data subject redress",
        "obligations": "mandatory requirements must shall required",
        "innovation": "sandbox voluntary flexible risk-based innovation",
        "transparency": "disclosure explainability audit transparency"
    }

    dimensional_breakdown = {}
    for dim_name, anchor_str in anchors.items():
        dim_emb = embed_text(anchor_str)
        norm_dim = np.linalg.norm(dim_emb)

        dot_p1 = np.dot(emb1, dim_emb)
        strength_p1 = float(dot_p1 / (norm1 * norm_dim)) if (norm1 > 0 and norm_dim > 0) else 0.0
        strength_p1 = max(0.0, strength_p1)

        dot_p2 = np.dot(emb2, dim_emb)
        strength_p2 = float(dot_p2 / (norm2 * norm_dim)) if (norm2 > 0 and norm_dim > 0) else 0.0
        strength_p2 = max(0.0, strength_p2)

        dominant = "policy1" if strength_p1 >= strength_p2 else "policy2"
        gap = abs(strength_p1 - strength_p2)

        dimensional_breakdown[dim_name] = {
            "strength_policy1": round(strength_p1, 4),
            "strength_policy2": round(strength_p2, 4),
            "dominant": dominant,
            "gap": round(gap, 4)
        }

    # Part D - Cross-encoder bilateral verdict normalized using sigmoid
    cross_encoder_failed = False
    cross_encoder_normalized = None
    if cross_encoder is not None:
        try:
            content1 = (p1.get("content") or "")[:512]
            content2 = (p2.get("content") or "")[:512]
            scores = cross_encoder.predict([(content1, content2)])
            raw_score = float(scores[0])
            # Apply standard sigmoid
            cross_encoder_normalized = 1.0 / (1.0 + math.exp(-raw_score))
        except Exception as e:
            logger.warning(f"Cross-Encoder prediction failed in comparator: {e}. Adjusting composite formula to 60% semantic + 40% jaccard.")
            cross_encoder_failed = True
    else:
        logger.warning("Cross-Encoder not loaded in comparator. Adjusting composite formula to 60% semantic + 40% jaccard.")
        cross_encoder_failed = True

    # Part E - Tag gap analysis (Jaccard)
    tags1 = set(p1["tags"])
    tags2 = set(p2["tags"])

    shared_tags = list(tags1.intersection(tags2))
    raw_only_p1 = tags1 - tags2
    raw_only_p2 = tags2 - tags1

    # Filter out tags that are actually mentioned in the other policy's content or title (case-insensitive)
    content1_lower = ((p1.get("content") or "") + " " + p1.get("title", "")).lower()
    content2_lower = ((p2.get("content") or "") + " " + p2.get("title", "")).lower()

    only_p1 = []
    for t in raw_only_p1:
        t_lower = t.lower()
        if t_lower not in content2_lower:
            only_p1.append(t)

    only_p2 = []
    for t in raw_only_p2:
        t_lower = t.lower()
        if t_lower not in content1_lower:
            only_p2.append(t)

    union_tags = tags1.union(tags2)
    jaccard = len(shared_tags) / len(union_tags) if union_tags else 0.0

    # Part F - Composite similarity score
    if cross_encoder_failed:
        composite_score = (semantic_similarity * 0.60) + (jaccard * 0.40)
        cross_val_to_return = None
    else:
        composite_score = (semantic_similarity * 0.40) + (cross_encoder_normalized * 0.35) + (jaccard * 0.25)
        cross_val_to_return = round(cross_encoder_normalized, 4)

    composite_score = round(min(max(composite_score, 0.0), 1.0), 4)

    # Assign similarity label
    if composite_score >= 0.8:
        similarity_label = "Nearly Identical"
    elif composite_score >= 0.65:
        similarity_label = "Highly Similar"
    elif composite_score >= 0.5:
        similarity_label = "Moderately Similar"
    elif composite_score >= 0.35:
        similarity_label = "Loosely Related"
    else:
        similarity_label = "Distinct Approaches"

    # Part G - Regulatory approach inference
    approach_p1 = _infer_approach(p1["tags"], p1["title"], p1["sector"])
    approach_p2 = _infer_approach(p2["tags"], p2["title"], p2["sector"])

    # Part H - Generate 5-7 dynamic insights
    insights = []

    # 1. Year Vintage Gap
    y1 = p1.get("year")
    y2 = p2.get("year")
    if y1 and y2:
        gap = abs(y1 - y2)
        if gap >= 3:
            older = p1["title"] if y1 < y2 else p2["title"]
            newer = p2["title"] if y1 < y2 else p1["title"]
            insights.append(
                f"Vintage Gap: There is a notable {gap}-year difference in publication date, "
                f"meaning '{newer}' may contain newer standards compared to '{older}'."
            )

    # 2. Region comparison
    if p1["country"] != p2["country"]:
        if p1["region"] != p2["region"]:
            insights.append(
                f"Geopolitical Divergence: Policies originate from different regions "
                f"({p1['country']} in {p1['region']} vs {p2['country']} in {p2['region']}), which strongly shapes their baseline priorities."
            )
        else:
            insights.append(
                f"Intra-regional Alignment: Both policies are developed within the {p1['region']} region, indicating potential regulatory harmony."
            )

    # 3. Sector comparison
    p1_clean_sec = "Healthcare & Clinical Trials" if p1["id"] == "fedreg_7715b10d6f" else p1["sector"]
    p2_clean_sec = "Healthcare & Clinical Trials" if p2["id"] == "fedreg_7715b10d6f" else p2["sector"]
    if p1_clean_sec != p2_clean_sec:
        insights.append(
            f"Cross-sector Mapping: Comparing '{p1['title']}' ({p1_clean_sec}) with '{p2['title']}' ({p2_clean_sec}) "
            f"identifies regulatory dynamics across distinct domains."
        )

    # 4. Dimensional highlights
    large_gaps = []
    for dim_name, info in dimensional_breakdown.items():
        if info["gap"] > 0.12:
            large_gaps.append((dim_name, info))
    
    if large_gaps:
        # Pick the largest gap to report
        large_gaps = sorted(large_gaps, key=lambda x: -x[1]["gap"])
        dim_name, info = large_gaps[0]
        dom_p = p1["title"] if info["dominant"] == "policy1" else p2["title"]
        sub_p = p2["title"] if info["dominant"] == "policy1" else p1["title"]
        insights.append(
            f"Emphasis Divergence: '{dom_p}' places significantly stronger emphasis on '{dim_name}' "
            f"(strength gap: {info['gap']:.2f}) compared to '{sub_p}'."
        )

    # 5. Tag gap insights
    if only_p1:
        insights.append(
            f"Unique Focus in P1: '{p1['title']}' includes explicit references to focus areas like {', '.join(only_p1[:3])} "
            f"omitted in the other document."
        )
    if only_p2:
        insights.append(
            f"Unique Focus in P2: '{p2['title']}' covers parameters such as {', '.join(only_p2[:3])} "
            f"not emphasized in the companion policy."
        )

    # 6. Word count density
    wc1 = len(p1["content"].split())
    wc2 = len(p2["content"].split())
    ratio = max(wc1, wc2) / min(wc1, wc2) if min(wc1, wc2) > 0 else 1.0
    if ratio > 1.8:
        longer = p1["title"] if wc1 > wc2 else p2["title"]
        shorter = p2["title"] if wc1 > wc2 else p1["title"]
        insights.append(
            f"Structural Complexity: '{longer}' represents a much more detailed text (word count: {max(wc1, wc2)}) "
            f"relative to the more concise '{shorter}' (word count: {min(wc1, wc2)})."
        )

    # 7. Strategic alignment vs Divergence insights
    if composite_score < 0.45:
        if p1_clean_sec != p2_clean_sec:
            insights.append(
                f"Conceptual Divergence: The policies address distinct regulatory spheres "
                f"({p1_clean_sec} vs. {p2_clean_sec}) with minimal shared provisions."
            )
        else:
            insights.append(
                f"Regulatory Divergence: Although sharing a broad sector, the policies govern "
                f"distinct operational scopes with a low composite overlap ({int(composite_score*100)}%)."
            )
    else:
        if approach_p1 == approach_p2:
            insights.append(
                f"Strategic Approach: Both policies align under a '{approach_p1}' philosophy, creating a unified regulatory mindset."
            )
        else:
            insights.append(
                f"Philosophy Shift: '{p1['title']}' takes a '{approach_p1}' approach, while '{p2['title']}' "
                f"employs a '{approach_p2}' regulatory methodology."
            )

    # Limit to 7 insights
    insights = insights[:7]

    # Part I - Generate Recommended Alignment Advice
    recs_and_alignment = []
    newer_title = p2["title"] if (y1 and y2 and y1 < y2) else p1["title"]

    if composite_score < 0.45:
        recs_and_alignment.append("Maintain separate compliance tracks: Due to low logical coherence, do not attempt to consolidate these regulations under a single workflow.")
        recs_and_alignment.append("Conduct independent stakeholder audits: Engage distinct legal/technical teams for each domain to prevent scope creep or cross-contamination.")
        recs_and_alignment.append("Avoid unified technology controls: Implement isolated security or procedural controls tailored specifically to each framework's unique demands.")
    else:
        if shared_tags:
            recs_and_alignment.append(f"Consolidate shared controls: Map the common parameters ({', '.join(shared_tags[:4])}) to a single compliance checklist to reduce audit overhead.")
        else:
            recs_and_alignment.append("Consolidate common clauses: Map the overlapping regulatory requirements to a single compliance checklist.")
        recs_and_alignment.append("Implement cross-training: Train compliance officers on both frameworks to leverage operational synergies.")
        recs_and_alignment.append(f"Future-proof against updates: Use the standards defined in the newer framework ('{newer_title}') to proactively update compliance workflows.")

    return {
        "policy1": {
            "id": p1["id"],
            "title": p1["title"],
            "sector": p1["sector"],
            "country": p1["country"],
            "region": p1["region"],
            "year": p1["year"],
            "tags": p1["tags"],
            "approach": approach_p1
        },
        "policy2": {
            "id": p2["id"],
            "title": p2["title"],
            "sector": p2["sector"],
            "country": p2["country"],
            "region": p2["region"],
            "year": p2["year"],
            "tags": p2["tags"],
            "approach": approach_p2
        },
        "overall_metrics": {
            "semantic_similarity": round(semantic_similarity, 4),
            "cross_encoder_normalized": cross_val_to_return,
            "jaccard_coefficient": round(jaccard, 4),
            "composite_score": composite_score,
            "similarity_label": similarity_label
        },
        "dimensional_breakdown": dimensional_breakdown,
        "shared_tags": shared_tags,
        "only_policy1_tags": only_p1,
        "only_policy2_tags": only_p2,
        "insights": insights,
        "recs_and_alignment": recs_and_alignment
    }


if __name__ == "__main__":
    print("[INFO] Running Policy Comparator V2 Test Suite...")
    
    conn = get_connection()
    try:
        # Load sample policies for testing
        all_p = conn.execute("SELECT id, title, sector, region FROM policies WHERE embedding IS NOT NULL").fetchall()
    finally:
        conn.close()

    # Find pairs programmatically
    # Pair 1: Same sector, same region
    pair1 = None
    for i in range(len(all_p)):
        for j in range(i+1, len(all_p)):
            if all_p[i]["sector"] == all_p[j]["sector"] and all_p[i]["region"] == all_p[j]["region"]:
                pair1 = (all_p[i]["id"], all_p[j]["id"], all_p[i]["title"], all_p[j]["title"])
                break
        if pair1:
            break

    # Pair 2: Same sector, different region
    pair2 = None
    for i in range(len(all_p)):
        for j in range(i+1, len(all_p)):
            if all_p[i]["sector"] == all_p[j]["sector"] and all_p[i]["region"] != all_p[j]["region"]:
                pair2 = (all_p[i]["id"], all_p[j]["id"], all_p[i]["title"], all_p[j]["title"])
                break
        if pair2:
            break

    # Pair 3: Cross sector
    pair3 = None
    for i in range(len(all_p)):
        for j in range(i+1, len(all_p)):
            if all_p[i]["sector"] != all_p[j]["sector"]:
                pair3 = (all_p[i]["id"], all_p[j]["id"], all_p[i]["title"], all_p[j]["title"])
                break
        if pair3:
            break

    test_pairs = [
        ("SAME SECTOR, SAME REGION", pair1),
        ("SAME SECTOR, DIFFERENT REGION", pair2),
        ("CROSS SECTOR", pair3)
    ]

    for label, pair in test_pairs:
        print("\n" + "=" * 90)
        print(f"PAIR CATEGORY: {label}")
        print("=" * 90)
        if not pair:
            print("[WARN] No appropriate pair found in database for this category.")
            continue
            
        id1, id2, t1, t2 = pair
        print(f"Policy 1: '{t1}' ({id1})")
        print(f"Policy 2: '{t2}' ({id2})")
        print("-" * 90)
        
        result = compare_policies_v2(id1, id2)
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
            
        metrics = result["overall_metrics"]
        print(f"Composite Score:      {metrics['composite_score']:.4f} ({metrics['similarity_label']})")
        print(f"  - Semantic Similarity: {metrics['semantic_similarity']:.4f}")
        print(f"  - Cross-Encoder Sigmoid: {metrics['cross_encoder_normalized']:.4f}")
        print(f"  - Jaccard Tag Similarity: {metrics['jaccard_coefficient']:.4f}")
        print("\nDimensional Breakdown:")
        for dim, info in result["dimensional_breakdown"].items():
            print(f"  {dim.capitalize():<15}: P1 Strength: {info['strength_policy1']:.4f} | P2 Strength: {info['strength_policy2']:.4f} | Gap: {info['gap']:.4f} (Dominant: {info['dominant']})")
            
        print("\nGenerated Insights:")
        for idx, insight in enumerate(result["insights"], 1):
            print(f"  {idx}. {insight}")
