from app.services.nlp_service import get_policy_by_id
from app.services.fine_extractor import extract_fines

def compare_policies(id1: str, id2: str) -> dict:
    p1 = get_policy_by_id(id1)
    p2 = get_policy_by_id(id2)
    if not p1 or not p2:
        return {"error": "One or both policies not found"}

    shared_tags = list(set(p1["tags"]) & set(p2["tags"]))
    unique_tags_p1 = list(set(p1["tags"]) - set(p2["tags"]))
    unique_tags_p2 = list(set(p2["tags"]) - set(p1["tags"]))
    same_sector = p1["sector"] == p2["sector"]
    same_region = p1.get("region") == p2.get("region")

    insights = []

    # ── Approach & Philosophy ─────────────────────────────────
    if same_sector:
        if p1.get("country") != p2.get("country"):
            insights.append(
                f"Both address {p1['sector']} but from different national contexts. "
                f"{p1['country']} takes a {'binding' if 'compliance' in p1.get('tags', []) else 'guidance-based'} approach "
                f"while {p2['country']} emphasizes {'enforcement' if 'enforcement' in p2.get('tags', []) else 'voluntary adoption'}."
            )
    else:
        insights.append(
            f"These policies address different problem spaces — "
            f"'{p1['sector']}' focuses on {_sector_focus(p1['sector'])} "
            f"while '{p2['sector']}' addresses {_sector_focus(p2['sector'])}. "
            f"Together they cover complementary aspects of digital governance."
        )

    # ── Unique Strengths ──────────────────────────────────────
    if unique_tags_p1:
        insights.append(
            f"'{p1['title'][:45]}...' uniquely addresses: "
            f"{', '.join(unique_tags_p1[:3])} — areas not covered by the other policy."
        )
    if unique_tags_p2:
        insights.append(
            f"'{p2['title'][:45]}...' distinctively focuses on: "
            f"{', '.join(unique_tags_p2[:3])} — giving it a different regulatory scope."
        )

    # ── Shared Ground ─────────────────────────────────────────
    if shared_tags:
        insights.append(
            f"Both policies converge on: {', '.join(shared_tags[:4])}. "
            f"This overlap suggests these are foundational concerns across different governance contexts."
        )
    else:
        insights.append(
            f"No overlapping focus areas — these policies are genuinely complementary "
            f"and could be adopted together without redundancy."
        )

    # ── Regulatory Maturity & Timeline ───────────────────────
    if p1.get("year") and p2.get("year"):
        diff = abs(p1["year"] - p2["year"])
        older = p1 if p1["year"] < p2["year"] else p2
        newer = p1 if p1["year"] > p2["year"] else p2
        if diff > 0:
            insights.append(
                f"'{newer['title'][:40]}...' ({newer['year']}) builds on {diff} year(s) of "
                f"regulatory evolution since '{older['title'][:40]}...' ({older['year']}). "
                f"The newer policy likely addresses gaps identified in earlier frameworks."
            )

    # ── Geographic & Jurisdictional ───────────────────────────
    if not same_region:
        insights.append(
            f"This is a cross-regional comparison: {p1.get('region')} ({p1['country']}) "
            f"vs {p2.get('region')} ({p2['country']}). "
            f"Regulatory approaches often reflect regional economic priorities and "
            f"governance traditions — direct transplantation may require adaptation."
        )
    else:
        insights.append(
            f"Both originate from {p1.get('region')} — suggesting regional regulatory "
            f"alignment or mutual influence in policy design."
        )

    # ── Enforcement Strength ──────────────────────────────────
    p1_enforcement = any(t in p1.get("tags", []) for t in ["compliance", "enforcement", "mandatory", "binding"])
    p2_enforcement = any(t in p2.get("tags", []) for t in ["compliance", "enforcement", "mandatory", "binding"])

    if p1_enforcement and not p2_enforcement:
        insights.append(
            f"'{p1['title'][:40]}...' has stronger enforcement mechanisms with binding obligations, "
            f"while '{p2['title'][:40]}...' leans toward voluntary adoption or principles-based guidance."
        )
    elif p2_enforcement and not p1_enforcement:
        insights.append(
            f"'{p2['title'][:40]}...' carries binding enforcement weight "
            f"compared to the more advisory nature of '{p1['title'][:40]}...'."
        )
    elif p1_enforcement and p2_enforcement:
        insights.append(
            f"Both policies carry significant enforcement obligations — "
            f"organizations operating across both jurisdictions face compounding compliance requirements."
        )

    # ── Penalty Fine Comparison ───────────────────────────────
    p1_fines = extract_fines(p1.get("content", ""))
    p2_fines = extract_fines(p2.get("content", ""))

    if p1_fines and p2_fines and p1_fines.get("has_fines") and p2_fines.get("has_fines"):
        insights.append(
            f"Both policies enforce financial penalties. "
            f"{p1['country']}: {p1_fines.get('summary', 'penalties apply')}. "
            f"{p2['country']}: {p2_fines.get('summary', 'penalties apply')}."
        )
    elif p1_fines and p1_fines.get("has_fines") and not (p2_fines and p2_fines.get("has_fines")):
        insights.append(
            f"'{p1['title'][:40]}...' enforces explicit financial penalties ({p1_fines.get('summary', '')}), "
            f"while '{p2['title'][:40]}...' does not specify monetary sanctions."
        )
    elif p2_fines and p2_fines.get("has_fines") and not (p1_fines and p1_fines.get("has_fines")):
        insights.append(
            f"'{p2['title'][:40]}...' enforces explicit financial penalties ({p2_fines.get('summary', '')}), "
            f"while '{p1['title'][:40]}...' does not specify monetary sanctions."
        )

    # ── Adoption Recommendation ───────────────────────────────
    if shared_tags and not same_sector:
        newer = p1 if (p1.get("year") or 0) > (p2.get("year") or 0) else p2
        older = p2 if newer == p1 else p1
        insights.append(
            f"Policy makers in emerging economies could prioritize "
            f"'{newer['title'][:40]}...' as a more current framework, "
            f"using '{older['title'][:40]}...' as foundational context."
        )

    return {
        "policy_1": {
            **{k: p1[k] for k in ["id", "title", "country", "sector", "region", "year", "tags", "status", "source_url"]},
            "penalty_fines": p1_fines
        },
        "policy_2": {
            **{k: p2[k] for k in ["id", "title", "country", "sector", "region", "year", "tags", "status", "source_url"]},
            "penalty_fines": p2_fines
        },
        "same_sector": same_sector,
        "shared_tags": shared_tags,
        "unique_to_policy_1": unique_tags_p1,
        "unique_to_policy_2": unique_tags_p2,
        "insights": insights,
    }


def _sector_focus(sector: str) -> str:
    """Returns a plain-language description of what each sector covers."""
    mapping = {
        "AI Governance":        "algorithmic accountability, AI risk management, and ethical deployment of AI systems",
        "Cybersecurity":        "threat detection, incident response, and protection of critical digital infrastructure",
        "Data Privacy":         "individual data rights, consent management, and protection of personal information",
        "Healthcare AI":        "safety of AI in clinical settings, medical device regulation, and patient data protection",
        "Financial Regulation": "model risk in financial AI, fair lending, and systemic risk from algorithmic trading",
        "POSH Policies":        "workplace harassment prevention, employee protection, and gender-based discrimination",
        "ESG Policies":         "environmental sustainability, social responsibility, and corporate governance reporting",
        "IoT and Robotics":     "connected device security, robotics safety standards, and IoT data governance",
    }
    return mapping.get(sector, "regulatory compliance and governance standards")