import sys
import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from data.country_profiles import COUNTRY_PROFILES
from app.database import get_connection

# ── Globals ──────────────────────────────────────────────────
_model        = None   # SentenceTransformer
_embeddings   = None   # policy embeddings matrix
_policy_data  = None   # list of policy dicts
_kmeans       = None
_country_embeddings = {}  # precomputed per-country need embeddings
N_CLUSTERS    = 6

# ── Country need descriptions for semantic matching ──────────
# These are rich text descriptions of what each country needs
# The model will semantically match policy content against these
COUNTRY_NEED_DESCRIPTIONS = {
    "Indonesia": (
        "Indonesia urgently needs cybersecurity incident response laws and mandatory "
        "breach reporting for critical infrastructure. The country lacks personal data "
        "protection legislation, cybersecurity standards for financial services, and "
        "AI governance frameworks for public sector automation."
    ),
    "Nigeria": (
        "Nigeria needs financial cybersecurity standards for fintech and mobile banking. "
        "Data protection enforcement for consumer financial data is critical. "
        "AI governance for automated lending decisions and fraud detection systems "
        "needs regulatory oversight."
    ),
    "Kenya": (
        "Kenya needs data privacy legislation for mobile money services and digital ID. "
        "Cybersecurity standards for mobile financial services and AI accountability "
        "for credit scoring algorithms used by millions of unbanked citizens."
    ),
    "Saudi Arabia": (
        "Saudi Arabia needs AI governance frameworks aligned with Vision 2030 smart city "
        "initiatives. Algorithmic accountability for government automated services, "
        "AI ethics standards for healthcare diagnostics, and cybersecurity for "
        "oil infrastructure and financial sector digital transformation."
    ),
    "United Arab Emirates": (
        "UAE needs data privacy legislation protecting residents from commercial "
        "data exploitation. AI ethics accountability for surveillance systems, "
        "automated government services transparency, and cybersecurity compliance "
        "standards for financial free zones and digital economy."
    ),
    "South Korea": (
        "South Korea needs comprehensive data privacy rights equivalent to GDPR. "
        "AI liability frameworks for autonomous vehicles and semiconductor AI systems. "
        "Cybersecurity mandatory audit requirements for critical infrastructure "
        "and supply chain security standards for technology exports."
    ),
    "Argentina": (
        "Argentina needs AI governance frameworks for public sector automated decisions. "
        "Modernized privacy law with stronger enforcement powers and data portability rights. "
        "Cybersecurity incident reporting obligations for financial institutions "
        "and critical infrastructure operators."
    ),
    "Brazil": (
        "Brazil needs mandatory cybersecurity incident reporting standards and "
        "critical infrastructure protection frameworks. AI governance for "
        "automated government benefit decisions affecting millions. "
        "LGPD enforcement strengthening for data broker regulation."
    ),
    "Mexico": (
        "Mexico needs cybersecurity standards for manufacturing supply chains and "
        "financial sector data protection enforcement. AI accountability for "
        "law enforcement predictive systems and privacy law modernization "
        "with stronger individual rights and enforcement capacity."
    ),
    "India": (
        "India needs mandatory cybersecurity incident reporting within defined timelines "
        "for critical sectors. AI accountability standards for facial recognition "
        "in public spaces and automated government welfare systems. "
        "Cross-border data transfer security frameworks complementing DPDP Act."
    ),
    "Japan": (
        "Japan needs binding AI safety requirements for high-risk systems replacing "
        "voluntary guidelines. Mandatory cybersecurity standards for critical "
        "infrastructure replacing sector-by-sector approaches. "
        "Algorithmic transparency requirements for automated hiring and credit decisions."
    ),
    "Australia": (
        "Australia needs privacy law reform giving individuals right to erasure and "
        "automated decision explanation. AI liability framework for high-risk government "
        "AI systems. Enhanced critical infrastructure cybersecurity obligations "
        "with mandatory security assessments for operators."
    ),
    "Canada": (
        "Canada needs mandatory cybersecurity incident reporting for private sector "
        "critical infrastructure. AI liability rules for high-impact automated decisions "
        "in employment and credit. PIPEDA replacement with stronger enforcement "
        "powers and meaningful consent requirements."
    ),
    "South Africa": (
        "South Africa needs cybersecurity incident response mandatory standards "
        "complementing POPIA data protection. AI governance frameworks for "
        "financial inclusion algorithms and public sector automation. "
        "Digital economy security standards for growing fintech sector."
    ),
    "United Kingdom": (
        "UK needs AI liability legislation for high-risk AI systems post-Brexit. "
        "Data adequacy maintenance with EU requiring privacy law alignment. "
        "Binding cybersecurity standards for critical national infrastructure "
        "and AI accountability for public sector automated decisions."
    ),
    "Germany": (
        "Germany needs AI quality standards for industrial manufacturing applications "
        "and explainability requirements for safety-critical AI systems. "
        "Supply chain cybersecurity audit requirements for automotive and machinery. "
        "Sovereign cloud security standards protecting industrial data."
    ),
    "France": (
        "France needs binding AI accountability rules for public sector algorithmic "
        "decisions and government AI transparency requirements. Cybersecurity "
        "standards for critical services and digital sovereignty protection "
        "frameworks preventing foreign data access."
    ),
    "Singapore": (
        "Singapore needs quantum-resilient cybersecurity standards for financial sector. "
        "AI accountability enforcement mechanisms beyond voluntary frameworks. "
        "Regional cross-border data governance leadership standards and "
        "binding AI liability rules for high-stakes automated decisions."
    ),
    "China": (
        "China needs international AI safety alignment frameworks enabling "
        "cross-border AI service interoperability. Data transfer standards "
        "compatible with global privacy frameworks. International cybersecurity "
        "cooperation standards reducing fragmentation."
    ),
    "United States": (
        "United States needs federal privacy legislation replacing fragmented state laws. "
        "AI liability standards for foundation model developers and deployers. "
        "Mandatory critical infrastructure cybersecurity baseline requirements "
        "and unified federal AI risk assessment framework."
    ),
    "European Union": (
        "European Union needs AI Act enforcement capacity building and "
        "quantum security standards for critical infrastructure. "
        "Cross-border cybersecurity incident coordination improvements and "
        "international data transfer adequacy framework modernization."
    ),
    "International": (
        "International bodies need global AI governance harmonization reducing "
        "regulatory fragmentation. Cross-border cybersecurity cooperation standards "
        "and harmonized data protection adequacy frameworks enabling digital trade."
    ),
}

def _load_and_train():
    global _model, _embeddings, _policy_data, _kmeans, _country_embeddings

    print("🔄 Loading Sentence Transformer model...")
    _model = SentenceTransformer('all-MiniLM-L6-v2')  # fast, good quality, 384 dims

    conn = get_connection()
    rows = conn.execute("SELECT * FROM policies").fetchall()
    conn.close()

    policies = []
    for row in rows:
        p = dict(row)
        p["tags"] = json.loads(p["tags"] or "[]")
        policies.append(p)

    # Build rich text representation for each policy
    policy_texts = []
    for p in policies:
        tags_text = " ".join(p["tags"])
        rich_text = (
            f"Title: {p['title']}. "
            f"Sector: {p['sector']}. "
            f"Country: {p['country']}. "
            f"Region: {p['region']}. "
            f"Focus areas: {tags_text}. "
            f"Content: {p['content']}"
        )
        policy_texts.append(rich_text)

    # Generate semantic embeddings for all policies
    print("🔄 Generating policy embeddings...")
    _embeddings = _model.encode(policy_texts, show_progress_bar=False)
    # _embeddings shape: (30, 384)

    # KMeans clustering on embeddings
    _kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    cluster_labels = _kmeans.fit_predict(_embeddings)

    for i, p in enumerate(policies):
        p["cluster"] = int(cluster_labels[i])
        p["embedding_idx"] = i

    _policy_data = policies

    # Precompute country need embeddings for semantic matching
    print("🔄 Computing country need embeddings...")
    for country, need_desc in COUNTRY_NEED_DESCRIPTIONS.items():
        _country_embeddings[country] = _model.encode([need_desc])[0]

    print(f"✅ Recommender trained: {len(policies)} policies, {N_CLUSTERS} clusters, {len(_country_embeddings)} country profiles")


def _ensure_trained():
    if _policy_data is None:
        _load_and_train()


def _calculate_need_score(country: str, policy: dict, policy_idx: int) -> float:
    profile = COUNTRY_PROFILES.get(country)
    if not profile:
        return 0.0

    if country == policy.get("country"):
        return 0.0

    # ── PURE SEMANTIC SCORE (0-1.0) ──────────────────────────
    # This is the ONLY primary driver
    if country not in _country_embeddings or _embeddings is None:
        return 0.0

    policy_emb = _embeddings[policy_idx].reshape(1, -1)
    country_emb = _country_embeddings[country].reshape(1, -1)
    semantic_sim = float(cosine_similarity(policy_emb, country_emb)[0][0])

    # ── PENALTY: Country already has similar content ──────────
    country_policy_indices = [
        i for i, p in enumerate(_policy_data)
        if p["country"] == country
    ]
    coverage_penalty = 0.0
    if country_policy_indices:
        country_embs = _embeddings[country_policy_indices]
        existing_sims = cosine_similarity(policy_emb, country_embs).flatten()
        max_existing = float(np.max(existing_sims))
        coverage_penalty = max_existing * 0.4  # strong penalty if already covered

    # ── SMALL MODIFIERS (max ±0.10 total) ────────────────────
    modifier = 0.0

    # Sector missing = small boost
    if policy["sector"] not in profile["existing_sectors"]:
        modifier += 0.05
    else:
        modifier -= 0.05  # penalty if already has sector

    # Maturity — very small adjustment
    maturity_adj = {"nascent": 0.05, "emerging": 0.03, "developing": 0.01, "advanced": -0.02}
    modifier += maturity_adj.get(profile["regulatory_maturity"], 0.0)

    # Final score = semantic - coverage_penalty + small modifiers
    score = semantic_sim - coverage_penalty + modifier

    return round(min(max(score, 0.0), 1.0), 3)

def _generate_reasoning(country: str, policy: dict, need_score: float) -> str:
    profile = COUNTRY_PROFILES.get(country, {})
    context = profile.get("context", "")
    maturity = profile.get("regulatory_maturity", "developing")
    sector = policy["sector"]
    missing = sector not in profile.get("existing_sectors", [])

    # Semantic similarity score interpretation
    if need_score > 0.6:
        relevance = "highly relevant"
    elif need_score > 0.4:
        relevance = "directly applicable"
    else:
        relevance = "potentially beneficial"

    parts = []

    if missing:
        parts.append(
            f"{country} has no dedicated {sector} framework, "
            f"making '{policy['title']}' from {policy['country']} {relevance} to their needs."
        )
    else:
        parts.append(
            f"While {country} has existing {sector} regulation, "
            f"'{policy['title']}' offers complementary approaches scoring {relevance} "
            f"via semantic analysis of their regulatory gaps."
        )

    # Add specific gap reasoning from country need description
    need_desc = COUNTRY_NEED_DESCRIPTIONS.get(country, "")
    if need_desc:
        # Extract first sentence as specific context
        first_sentence = need_desc.split('.')[0] + "."
        parts.append(first_sentence)

    if maturity in ("nascent", "emerging"):
        parts.append(
            f"With {maturity} regulatory maturity, {country} can adopt "
            f"this proven framework rather than building from scratch."
        )

    return " ".join(parts)


def _generate_benefits(policy: dict, country: str, semantic_score: float) -> list:
    """Generate benefits based on actual policy content + country context."""
    profile = COUNTRY_PROFILES.get(country, {})
    sector = policy["sector"]
    tags = policy.get("tags", [])
    priority_needs = profile.get("priority_needs", [])
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

    # Add country-tier specific benefit
    if gdp_tier == "emerging" and len(benefits) < 4:
        benefits.append(
            "Leapfrogging regulatory development by adopting proven international frameworks"
        )

    return benefits[:4]


def get_recommendations(policy_id: str, top_n: int = 6) -> dict:
    _ensure_trained()

    target = next((p for p in _policy_data if p["id"] == policy_id), None)
    if not target:
        return {"error": f"Policy '{policy_id}' not found"}

    target_idx = target["embedding_idx"]
    target_emb = _embeddings[target_idx].reshape(1, -1)

    # Find similar policies via semantic similarity
    all_sims = cosine_similarity(target_emb, _embeddings).flatten()
    similar = []
    for i, sim in enumerate(all_sims):
        if i != target_idx and sim > 0.3:
            p = _policy_data[i]
            similar.append({
                "id": p["id"],
                "title": p["title"],
                "country": p["country"],
                "sector": p["sector"],
                "year": p.get("year"),
                "similarity": round(float(sim), 3)
            })
    similar = sorted(similar, key=lambda x: -x["similarity"])[:5]

    # Score all countries
    scored = []
    for country, profile in COUNTRY_PROFILES.items():
        if country == target["country"]:
            continue
        need = _calculate_need_score(country, target, target_idx)
        if need < 0.05:
            continue
        scored.append({
            "country": country,
            "region": profile.get("region", "Unknown"),
            "need_score": need,
            "regulatory_maturity": profile.get("regulatory_maturity", "unknown"),
            "reasoning": _generate_reasoning(country, target, need),
            "expected_benefits": _generate_benefits(target, country, need),
            "already_has_sector": target["sector"] in profile.get("existing_sectors", []),
            "priority_needs": profile.get("priority_needs", []),
        })

    top = sorted(scored, key=lambda x: -x["need_score"])[:top_n]

    return {
        "source_policy": {
            "id": target["id"],
            "title": target["title"],
            "sector": target["sector"],
            "country": target["country"],
            "tags": target["tags"],
            "cluster": target.get("cluster"),
        },
        "similar_policies": similar,
        "recommendations": top,
        "total_countries_analyzed": len(COUNTRY_PROFILES),
        "ml_method": "Sentence Transformers (all-MiniLM-L6-v2) + KMeans + Semantic Need-Gap Scoring"
    }


def get_recommendations_for_text(text: str, tags: list, title: str, top_n: int = 6) -> dict:
    _ensure_trained()

    tags_text = " ".join(tags)
    rich_text = f"Title: {title}. Focus areas: {tags_text}. Content: {text}"

    upload_emb = _model.encode([rich_text])

    # Similar policies
    sims = cosine_similarity(upload_emb, _embeddings).flatten()
    similar = []
    for i, sim in enumerate(sims):
        if sim > 0.2:
            p = _policy_data[i]
            similar.append({
                "id": p["id"],
                "title": p["title"],
                "country": p["country"],
                "sector": p["sector"],
                "year": p.get("year"),
                "similarity": round(float(sim), 3)
            })
    similar = sorted(similar, key=lambda x: -x["similarity"])[:5]

    top_sector = similar[0]["sector"] if similar else "AI Governance"

    temp_policy = {
        "id": "uploaded",
        "title": title,
        "content": text,
        "tags": tags,
        "sector": top_sector,
        "country": "Unknown",
        "year": None,
        "embedding_idx": None,
    }

    # For uploaded text, compute embedding on the fly
    upload_emb_vec = upload_emb[0]

    scored = []
    for country, profile in COUNTRY_PROFILES.items():
        score = 0.0

        # Semantic match against country needs
        if country in _country_embeddings:
            country_emb = _country_embeddings[country].reshape(1, -1)
            sem_sim = float(cosine_similarity(upload_emb, country_emb)[0][0])
            score += sem_sim * 0.50

        # Sector gap
        if top_sector not in profile["existing_sectors"]:
            score += 0.25
        else:
            score += 0.05

        # Maturity
        maturity_map = {"nascent": 0.15, "emerging": 0.10, "developing": 0.05, "advanced": 0.01}
        score += maturity_map.get(profile["regulatory_maturity"], 0.05)

        # Existing coverage penalty
        country_indices = [i for i, p in enumerate(_policy_data) if p["country"] == country]
        if country_indices:
            country_embs = _embeddings[country_indices]
            existing_sims = cosine_similarity(upload_emb, country_embs).flatten()
            score -= float(np.max(existing_sims)) * 0.20

        score = round(min(max(score, 0.0), 1.0), 3)
        if score < 0.05:
            continue

        scored.append({
            "country": country,
            "region": profile.get("region", "Unknown"),
            "need_score": score,
            "regulatory_maturity": profile.get("regulatory_maturity", "unknown"),
            "reasoning": _generate_reasoning(country, temp_policy, score),
            "expected_benefits": _generate_benefits(temp_policy, country, score),
            "already_has_sector": top_sector in profile.get("existing_sectors", []),
            "priority_needs": profile.get("priority_needs", []),
        })

    top = sorted(scored, key=lambda x: -x["need_score"])[:top_n]

    return {
        "recommendations": top,
        "similar_policies": similar,
        "detected_sector": top_sector,
        "ml_method": "Sentence Transformers (all-MiniLM-L6-v2) + Semantic Need-Gap Scoring"
    }
def get_recommendations_for_text(text: str, tags: list, title: str, top_n: int = 6) -> dict:
    _ensure_trained()

    tags_text = " ".join(tags)
    rich_text = f"Title: {title}. Focus areas: {tags_text}. Content: {text}"

    # Use Sentence Transformer instead of _vectorizer
    upload_emb = _model.encode([rich_text])

    # Similar policies via semantic similarity
    sims = cosine_similarity(upload_emb, _embeddings).flatten()
    similar = []
    for i, sim in enumerate(sims):
        if sim > 0.2:
            p = _policy_data[i]
            similar.append({
                "id": p["id"],
                "title": p["title"],
                "country": p["country"],
                "sector": p["sector"],
                "year": p.get("year"),
                "similarity": round(float(sim), 3)
            })
    similar = sorted(similar, key=lambda x: -x["similarity"])[:5]

    top_sector = similar[0]["sector"] if similar else "AI Governance"

    temp_policy = {
        "id": "uploaded",
        "title": title,
        "content": text,
        "tags": tags,
        "sector": top_sector,
        "country": "Unknown",
        "year": None,
        "embedding_idx": None,
    }

    scored = []
    for country, profile in COUNTRY_PROFILES.items():
        score = 0.0

        if country in _country_embeddings:
            country_emb = _country_embeddings[country].reshape(1, -1)
            sem_sim = float(cosine_similarity(upload_emb, country_emb)[0][0])
            score += sem_sim * 0.50

        if top_sector not in profile["existing_sectors"]:
            score += 0.05
        else:
            score -= 0.05

        maturity_map = {"nascent": 0.05, "emerging": 0.03, "developing": 0.01, "advanced": -0.02}
        score += maturity_map.get(profile["regulatory_maturity"], 0.0)

        country_indices = [i for i, p in enumerate(_policy_data) if p["country"] == country]
        if country_indices:
            country_embs = _embeddings[country_indices]
            existing_sims = cosine_similarity(upload_emb, country_embs).flatten()
            score -= float(np.max(existing_sims)) * 0.40

        score = round(min(max(score, 0.0), 1.0), 3)
        if score < 0.05:
            continue

        scored.append({
            "country": country,
            "region": profile.get("region", "Unknown"),
            "need_score": score,
            "regulatory_maturity": profile.get("regulatory_maturity", "unknown"),
            "reasoning": _generate_reasoning(country, temp_policy, score),
            "expected_benefits": _generate_benefits(temp_policy, country, score),
            "already_has_sector": top_sector in profile.get("existing_sectors", []),
            "priority_needs": profile.get("priority_needs", []),
        })

    top = sorted(scored, key=lambda x: -x["need_score"])[:top_n]

    return {
        "recommendations": top,
        "similar_policies": similar,
        "detected_sector": top_sector,
        "ml_method": "Sentence Transformers (all-MiniLM-L6-v2) + Semantic Need-Gap Scoring"
    }

def get_cluster_summary() -> dict:
    _ensure_trained()
    clusters = {}
    for p in _policy_data:
        c = str(p["cluster"])
        if c not in clusters:
            clusters[c] = []
        clusters[c].append({
            "id": p["id"],
            "title": p["title"],
            "sector": p["sector"]
        })
    return clusters