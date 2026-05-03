from fastapi import APIRouter
from pydantic import BaseModel
import json
from app.database import get_connection
from app.services.recommender import _ensure_trained
from app.services.nlp_service import load_policies

router = APIRouter()

class GenerateRequest(BaseModel):
    country: str
    sector: str

@router.post("/policy-template")
def generate_policy_template(req: GenerateRequest):
    _ensure_trained()
    
    conn = get_connection()
    row = conn.execute("SELECT * FROM country_profiles WHERE country = %s", (req.country,)).fetchone()
    conn.close()

    if not row:
        return {"error": "Country not found"}

    profile = {
        "region": row['region'],
        "gdp_tier": row['gdp_tier'],
        "regulatory_maturity": row['regulatory_maturity'],
        "context": row['context'],
        "priority_needs": json.loads(row['priority_needs']),
        "existing_sectors": json.loads(row['existing_sectors'])
    }

    # Find similar existing policies for reference
    policies = load_policies(sector=req.sector)
    if not policies:
        return {"error": "No policies found for this sector"}

    # Get top 3 most relevant existing policies
    reference_policies = policies[:3]

    # Extract common tags from reference policies
    all_tags = []
    for p in reference_policies:
        all_tags.extend(p.get("tags", []))

    from collections import Counter
    common_tags = [tag for tag, count in Counter(all_tags).most_common(8)]

    maturity = profile.get("regulatory_maturity", "developing")
    context = profile.get("context", "")
    priority_needs = profile.get("priority_needs", [])
    existing = profile.get("existing_sectors", [])

    # Dynamic Section Generation based on semantic tags of reference policies
    sections = ["1. Purpose and Scope", "2. Definitions and Key Terms"]
    for i, tag in enumerate(common_tags[:6]):
        sections.append(f"{i+3}. {tag.title()} Standards")
    sections.extend([
        f"{len(sections)+1}. Enforcement Mechanisms",
        f"{len(sections)+2}. Review and Amendment Procedures"
    ])
    
    if maturity in ("nascent", "emerging"):
        sections.append(f"{len(sections)+1}. Capacity Building and Technical Assistance")

    # Dynamic Requirements derived from top reference policies
    key_reqs = []
    for p in reference_policies:
        if p.get("key_requirements"):
            key_reqs.extend(json.loads(p["key_requirements"]))
    
    if not key_reqs:
        # Fallback dynamic logic if NLP pipeline hasn't run yet
        key_reqs = [
            f"Establish national regulatory authority for {req.sector}",
            f"Mandate minimum baselines for {common_tags[0] if common_tags else 'core operations'}",
            f"Implement risk-based classification frameworks",
            f"Require mandatory incident and compliance reporting"
        ]
        if maturity == "nascent":
            key_reqs.append("Seek international technical assistance for implementation")

    # Dynamic Timeline derived from maturity and sector
    timeline = {}
    if maturity == "nascent" or maturity == "emerging":
        timeline = {
            "Phase 1 (0-12 months)": "Establish regulatory authority and draft legislation",
            "Phase 2 (12-24 months)": "Consult stakeholders and finalize law",
            "Phase 3 (24-36 months)": "Pilot implementation with major organizations",
            "Phase 4 (36-48 months)": "Full enforcement and capacity review"
        }
    else:
        timeline = {
            "Phase 1 (0-6 months)": "Legislative amendments and regulatory update",
            "Phase 2 (6-12 months)": "Industry guidance and compliance tools",
            "Phase 3 (12-18 months)": "Full enforcement with monitoring"
        }

    # Build template
    template = {
        "country": req.country,
        "sector": req.sector,
        "suggested_title": f"{req.country} {req.sector} Framework — Draft Policy",
        "policy_context": context,
        "regulatory_gap": req.sector not in existing,
        "maturity_level": maturity,
        "recommended_tags": common_tags,
        "priority_areas": priority_needs,
        "recommended_sections": sections,
        "reference_policies": [
            {
                "id": p["id"],
                "title": p["title"],
                "country": p["country"],
                "source_url": p.get("source_url", "")
            }
            for p in reference_policies
        ],
        "key_requirements": list(set(key_reqs))[:5],
        "implementation_timeline": timeline,
    }

    return template