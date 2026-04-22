from app.services.nlp_service import get_policy_by_id

def compare_policies(id1: str, id2: str):
    p1 = get_policy_by_id(id1)
    p2 = get_policy_by_id(id2)
    if not p1 or not p2:
        return {"error": "One or both policies not found"}

    shared_tags = list(set(p1["tags"]) & set(p2["tags"]))
    same_sector = p1["sector"] == p2["sector"]
    same_region = p1.get("region") == p2.get("region")

    insights = []
    if same_sector:
        insights.append(f"Both policies govern the '{p1['sector']}' sector.")
    else:
        insights.append(f"Cross-sector comparison: '{p1['sector']}' vs '{p2['sector']}'.")
    if shared_tags:
        insights.append(f"Shared focus areas: {', '.join(shared_tags)}.")
    else:
        insights.append("No overlapping focus areas — distinct policy approaches.")
    if p1.get("year") and p2.get("year"):
        diff = abs(p1["year"] - p2["year"])
        newer = p1 if p1["year"] > p2["year"] else p2
        if diff > 0:
            insights.append(f"'{newer['title']}' is more recent by {diff} year(s).")
    if not same_region:
        insights.append(
            f"Geographic diversity: {p1.get('region')} ({p1['country']}) "
            f"vs {p2.get('region')} ({p2['country']})."
        )
    if p1.get("status") != p2.get("status"):
        insights.append(
            f"Status difference: {p1['title']} is '{p1.get('status')}' "
            f"while {p2['title']} is '{p2.get('status')}'."
        )

    return {
        "policy_1": {k: p1[k] for k in ["id","title","country","sector","region","year","tags","status","source_url"]},
        "policy_2": {k: p2[k] for k in ["id","title","country","sector","region","year","tags","status","source_url"]},
        "same_sector": same_sector,
        "shared_tags": shared_tags,
        "insights": insights,
    }