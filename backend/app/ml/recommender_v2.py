import sys
import json
import logging
import numpy as np
from pathlib import Path

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedder import embed_text, LOADED_MODEL_NAME
from app.ml.vector_store import search_similar_chroma
from data.country_profiles import COUNTRY_PROFILES

logger = logging.getLogger(__name__)

if LOADED_MODEL_NAME != "nlpaueb/legal-bert-base-uncased":
    logger.warning(f"Legal-BERT failed to load; using fallback bi-encoder model: {LOADED_MODEL_NAME}")

# Load need descriptions dynamically from database
def load_country_needs_from_db() -> dict:
    conn = get_connection()
    needs = {}
    try:
        rows = conn.execute("SELECT * FROM country_needs").fetchall()
        for r in rows:
            needs[r['country']] = r['description']
    except Exception as e:
        print(f"Error loading country needs: {e}")
    finally:
        conn.close()
    return needs

COUNTRY_NEED_DESCRIPTIONS = load_country_needs_from_db()


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


# 3. Upgraded Reasoning and Benefits helpers referencing the new scores
def _generate_reasoning(country: str, policy: dict, need_score: float, score_breakdown: dict) -> str:
    profile = COUNTRY_PROFILES.get(country, {})
    maturity = profile.get("regulatory_maturity", "developing")
    sector = policy["sector"]
    already_has = sector in _parse_list(profile.get("existing_sectors", []))

    if need_score > 0.6:
        relevance = "highly relevant"
    elif need_score > 0.4:
        relevance = "directly applicable"
    else:
        relevance = "potentially beneficial"

    parts = []

    # Factor 1: Sector Gap
    if not already_has:
        parts.append(
            f"{country} lacks an established {sector} framework (sector gap score: {score_breakdown['sector_gap']:.2f}), "
            f"making '{policy['title']}' from {policy['country']} {relevance}."
        )
    else:
        parts.append(
            f"Although {country} has existing {sector} regulation (sector gap score: {score_breakdown['sector_gap']:.2f}), "
            f"this policy represents a valuable addition offering complementary regulatory standards."
        )

    # Factor 2: Regulatory Maturity
    parts.append(
        f"With a {maturity} regulatory maturity level (maturity score: {score_breakdown['regulatory_maturity']:.2f}), "
        f"{country} has the capability to adapt this model."
    )

    # Factor 3: Semantic Need Match
    if score_breakdown["semantic_need"] > 0.08:
        parts.append(
            f"Semantic analysis indicates alignment (semantic score: {score_breakdown['semantic_need']:.2f}) "
            f"with priority national goals."
        )

    # Factor 4: Regional Pressure
    if score_breakdown["regional_pressure"] > 0.0:
        parts.append(
            f"Regional adoption pressure is active (regional score: {score_breakdown['regional_pressure']:.2f}) "
            f"due to nearby peers implementing similar frameworks."
        )

    # Factor 5: Economic Tier Alignment
    if score_breakdown["economic_tier"] >= 0.08:
        parts.append("Transferability is boosted by advanced-to-emerging leapfrogging opportunities.")

    return " ".join(parts)


def _generate_benefits(policy: dict, country: str, score_breakdown: dict) -> list:
    profile = COUNTRY_PROFILES.get(country, {})
    sector = policy["sector"]
    tags = policy.get("tags", [])
    gdp_tier = profile.get("gdp_tier", "emerging")

    benefits = []

    # Sector-specific benefits
    sector_benefits = {
        "AI Governance": [
            "Structured AI risk assessment framework reducing deployment risks",
            "Transparent algorithmic decision-making building public trust",
            "Legal clarity for AI developers and deployers",
            "International regulatory alignment enabling cross-border AI services",
        ],
        "Cybersecurity": [
            "Mandatory incident reporting enabling faster national threat response",
            "Standardized security baselines protecting critical infrastructure",
            "Clear liability framework for cybersecurity failures",
            "Enhanced resilience against state-sponsored cyberattacks",
        ],
        "Data Privacy": [
            "Individual data rights restoring citizen trust in digital services",
            "Mandatory breach notification reducing harm from data incidents",
            "International data transfer adequacy enabling digital trade",
            "Compliance framework attracting privacy-conscious foreign investment",
        ],
    }

    # Add sector-specific benefits
    base_benefits = sector_benefits.get(sector, [])
    benefits.extend(base_benefits[:2])

    # Add tag-specific benefits
    tag_benefit_map = {
        "transparency": "Increased accountability through mandatory transparency requirements",
        "safety": "Enhanced safety standards protecting citizens from algorithmic harm",
        "human oversight": "Human review mechanisms for high-stakes automated decisions",
        "risk": "Systematic risk management reducing operational and legal exposure",
        "incident reporting": "Coordinated incident response minimizing breach impact",
        "data localization": "Sovereign data control strengthening national security",
        "accountability": "Clear liability rules deterring negligent AI and data practices",
        "ethics": "Ethical AI principles embedded in national digital governance",
        "innovation": "Regulatory clarity enabling responsible innovation ecosystem",
        "compliance": "Harmonized compliance reducing cross-border friction",
    }

    for tag in tags:
        for keyword, benefit in tag_benefit_map.items():
            if keyword in tag.lower() and benefit not in benefits:
                benefits.append(benefit)
                break

    # Add economic tier alignment benefit
    if score_breakdown["economic_tier"] >= 0.08:
        benefits.append("Highly effective model transfer matching advanced economy standards into emerging markets")
    elif gdp_tier == "emerging" and len(benefits) < 4:
        benefits.append("Leapfrogging regulatory development by adopting proven international frameworks")

    return benefits[:4]


# 1. Score Country using the 5-Factor Scoring System
def score_country(country: str, policy: dict, similar_policies: list) -> dict or None:
    # Skip if same country as policy origin
    if country == policy.get("country"):
        return None

    profile = COUNTRY_PROFILES.get(country)
    if not profile:
        return None

    # Retrieve source policy GDP profile
    source_country = policy.get("country", "")
    source_profile = COUNTRY_PROFILES.get(source_country, {})

    # ==========================================
    # Factor 1: Sector Gap (weight 0.35)
    # ==========================================
    existing_sectors = _parse_list(profile.get("existing_sectors", []))
    sector = policy["sector"]

    if sector not in existing_sectors:
        factor1_score = 0.35
    else:
        # Check vintage of existing policy in that sector for this country
        max_year = None
        conn = get_connection()
        try:
            cur = conn.execute(
                "SELECT MAX(year) as max_yr FROM policies WHERE country = %s AND sector = %s AND year IS NOT NULL",
                (country, sector)
            )
            row = cur.fetchone()
            max_year = row["max_yr"] if row else None
        finally:
            conn.close()

        policy_year = policy.get("year") or 2026
        if max_year is not None and (policy_year - max_year) >= 3:
            factor1_score = 0.15
        else:
            factor1_score = 0.05

    # ==========================================
    # Factor 2: Regulatory Maturity Gap (weight 0.25)
    # ==========================================
    maturity = str(profile.get("regulatory_maturity", "developing")).lower()
    maturity_scores = {
        "nascent": 0.25,
        "emerging": 0.20,
        "developing": 0.12,
        "advanced": 0.04
    }
    factor2_score = maturity_scores.get(maturity, 0.12)

    # ==========================================
    # Factor 3: Semantic Need Match (weight 0.20)
    # ==========================================
    priority_needs = _parse_list(profile.get("priority_needs", []))
    needs_str = " ".join(priority_needs)
    need_desc = COUNTRY_NEED_DESCRIPTIONS.get(country, "")
    if need_desc:
        needs_str += " " + need_desc
    needs_str = needs_str.strip()

    tags_str = " ".join(_parse_list(policy.get("tags", [])))
    policy_str = f"Title: {policy['title']}. Tags: {tags_str}"

    if needs_str:
        # Generate embeddings
        needs_vector = embed_text(needs_str)
        policy_vector = embed_text(policy_str)

        # Cosine similarity
        dot = np.dot(needs_vector, policy_vector)
        norm_n = np.linalg.norm(needs_vector)
        norm_p = np.linalg.norm(policy_vector)
        cosine_sim = dot / (norm_n * norm_p) if (norm_n > 0 and norm_p > 0) else 0.0
        cosine_sim = max(0.0, float(cosine_sim))
        factor3_score = cosine_sim * 0.20
    else:
        factor3_score = 0.0

    # ==========================================
    # Factor 4: Regional Adoption Pressure (weight 0.12)
    # ==========================================
    target_region = profile.get("region")
    regional_adopters = 0
    for p in similar_policies:
        sim = float(p.get("approx_similarity", p.get("similarity", 0.0)))
        if sim > 0.5 and p.get("region") == target_region:
            regional_adopters += 1

    factor4_score = min(regional_adopters * 0.04, 0.12)

    # ==========================================
    # Factor 5: Economic Tier Alignment (weight 0.08)
    # ==========================================
    source_gdp = str(source_profile.get("gdp_tier", "emerging")).lower()
    target_gdp = str(profile.get("gdp_tier", "emerging")).lower()

    if source_gdp == "advanced" and target_gdp in ("emerging", "developing"):
        factor5_score = 0.08
    elif source_gdp == target_gdp:
        factor5_score = 0.05
    elif source_gdp in ("emerging", "developing") and target_gdp == "advanced":
        factor5_score = 0.02
    else:
        factor5_score = 0.05

    # ==========================================
    # Final Score Calculation
    # ==========================================
    need_score = factor1_score + factor2_score + factor3_score + factor4_score + factor5_score
    need_score = round(min(max(need_score, 0.0), 1.0), 3)

    score_breakdown = {
        "sector_gap": round(factor1_score, 4),
        "regulatory_maturity": round(factor2_score, 4),
        "semantic_need": round(factor3_score, 4),
        "regional_pressure": round(factor4_score, 4),
        "economic_tier": round(factor5_score, 4)
    }

    return {
        "country": country,
        "region": profile.get("region", "Unknown"),
        "need_score": need_score,
        "score_breakdown": score_breakdown,
        "regulatory_maturity": profile.get("regulatory_maturity", "unknown"),
        "already_has_sector": sector in existing_sectors,
        "reasoning": _generate_reasoning(country, policy, need_score, score_breakdown),
        "expected_benefits": _generate_benefits(policy, country, score_breakdown),
        "priority_needs": priority_needs
    }


# 2. Get Recommendations upgraded pipeline
def get_recommendations_v2(policy_id: str, top_n: int = 6) -> dict:
    # Load policy from PostgreSQL
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, tags, year, status, cluster_id
            FROM policies
            WHERE id = %s
            """,
            (policy_id,)
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {"error": f"Policy '{policy_id}' not found"}

    target = dict(row)
    target["tags"] = _parse_list(target.get("tags"))

    # Stage 1: search_similar_chroma(policy_id, n=20)
    try:
        similar_policies = search_similar_chroma(policy_id, n=20)
    except Exception as e:
        logger.warning(f"ChromaDB search failed, falling back to pgvector: {e}")
        try:
            from app.ml.embedding_store import get_embedding, find_similar_by_vector
            emb = get_embedding(policy_id)
            if emb is not None:
                raw_sim = find_similar_by_vector(emb, n=20, exclude_id=policy_id)
                similar_policies = []
                for r in raw_sim:
                    similar_policies.append({
                        "id": r["id"],
                        "title": r["title"],
                        "sector": r["sector"],
                        "country": r["country"],
                        "region": r["region"],
                        "approx_similarity": r["similarity_score"]
                    })
            else:
                similar_policies = []
        except Exception as pg_err:
            logger.error(f"Fallback pgvector search also failed: {pg_err}")
            similar_policies = []

    # Stage 2: score_country() for every country in profiles
    scored = []
    for country in COUNTRY_PROFILES.keys():
        res = score_country(country, target, similar_policies)
        if res:
            scored.append(res)

    # Stage 3: sort by need_score, take top top_n * 2
    scored = sorted(scored, key=lambda x: -x["need_score"])
    top_candidates = scored[:top_n * 2]

    # Stage 4: if top scores within 0.15 of each other, run reranking
    if len(top_candidates) > 1:
        highest = top_candidates[0]["need_score"]
        lowest = top_candidates[-1]["need_score"]

        if (highest - lowest) <= 0.15:
            # Temporary field 'content' for CrossEncoder
            for c in top_candidates:
                c["content"] = COUNTRY_NEED_DESCRIPTIONS.get(c["country"], "") or c["reasoning"]

            query_text = target.get("content") or ""
            
            try:
                from app.ml.embedder import rerank_with_cross_encoder, cross_encoder
                if cross_encoder is None:
                    raise ValueError("Cross-Encoder model is not loaded (None)")
                reranked = rerank_with_cross_encoder(query_text, top_candidates)
                top_candidates = reranked
            except Exception as ce_err:
                logger.warning(f"Cross-encoder reranking failed: {ce_err}. Skipping reranking step.")
            finally:
                # Cleanup temp field
                for c in top_candidates:
                    c.pop("content", None)

    # Stage 5: return top_n after reranking
    recommendations = top_candidates[:top_n]

    return {
        "source_policy": {
            "id": target["id"],
            "title": target["title"],
            "sector": target["sector"],
            "country": target["country"],
            "tags": target["tags"],
            "cluster": target.get("cluster_id"),
        },
        "similar_policies": similar_policies[:5],  # return top 5
        "recommendations": recommendations,
        "total_countries_analyzed": len(COUNTRY_PROFILES),
        "ml_method": "ChromaDB Cosine Search + 5-Factor Scoring System + Cross-Encoder Reranking"
    }


if __name__ == "__main__":
    print("[INFO] Running recommender test suite...")
    
    # Get 3 policies from different sectors
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector 
            FROM policies 
            WHERE embedding IS NOT NULL
            """
        )
        all_p = cur.fetchall()
    finally:
        conn.close()
    
    # Group by sector to select 3 different ones
    by_sector = {}
    for r in all_p:
        by_sector[r["sector"]] = r
    
    sample_policies = list(by_sector.values())[:3]
    
    for p in sample_policies:
        pid = p["id"]
        title = p["title"]
        sector = p["sector"]
        print("\n" + "=" * 80)
        print(f"TESTING RECOMMENDATIONS FOR: '{title}' ({pid})")
        print(f"Sector: {sector}")
        print("=" * 80)
        
        recs = get_recommendations_v2(pid, top_n=3)
        if "error" in recs:
            print(f"Error: {recs['error']}")
            continue
            
        print(f"ML Method: {recs['ml_method']}")
        print(f"Total similar policies in index: {len(recs['similar_policies'])}")
        print("\nTop 3 Recommendations:")
        for idx, rec in enumerate(recs["recommendations"], 1):
            print(f"\n  #{idx}: Country: {rec['country']} | Score: {rec['need_score']:.4f}")
            print(f"      Maturity: {rec['regulatory_maturity']} | Already Has Sector: {rec['already_has_sector']}")
            print(f"      Score Breakdown: {rec['score_breakdown']}")
            print(f"      Reasoning: {rec['reasoning']}")
            print(f"      Expected Benefits:")
            for b in rec["expected_benefits"]:
                print(f"        - {b}")
