"""
Paper Analysis Script for PolicyIQ IEEE Manuscript
===================================================
1. TF-IDF Baseline Comparison  (Table: Baseline vs. PolicyIQ V2)
2. Ablation Study              (Table: MCDA Factor Ablation)
3. Country Profiles Table T4   (6 representative rows from 21 profiles)

Run from backend/:  ../.venv/Scripts/python scripts/paper_analysis.py
"""
import sys, json
from pathlib import Path
import numpy as np

_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.recommender_v2 import (
    get_recommendations_v2, DEFAULT_WEIGHTS, score_country,
    COUNTRY_PROFILES, COUNTRY_NEED_DESCRIPTIONS,
    get_country_need_vector, _parse_list
)
from app.ml.embedder import embed_text
from app.ml.vector_store import search_similar_chroma

# ======================================================================
# HELPER: Load a sample of test policies (10 per sector, 3 sectors)
# ======================================================================
def load_test_policies():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, title, sector, country, region, content, tags, year, status
        FROM policies
        WHERE sector IN ('AI Governance', 'Cybersecurity', 'Data Privacy')
          AND embedding IS NOT NULL
        ORDER BY sector, id
    """).fetchall()
    conn.close()

    by_sector = {}
    for r in rows:
        sec = r["sector"]
        if sec not in by_sector:
            by_sector[sec] = []
        if len(by_sector[sec]) < 10:
            d = dict(r)
            d["tags"] = _parse_list(d.get("tags"))
            by_sector[sec].append(d)

    policies = []
    for sec in ["AI Governance", "Cybersecurity", "Data Privacy"]:
        policies.extend(by_sector.get(sec, []))
    return policies


# ======================================================================
# 1. TF-IDF BASELINE RECOMMENDER
# ======================================================================
def run_tfidf_baseline(test_policies):
    """
    Pure TF-IDF + cosine similarity baseline.
    For each policy, build a TF-IDF vector from title+tags+content,
    compute cosine similarity against each country's need description,
    and rank countries by raw similarity. No MCDA factors at all.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Build country need corpus
    country_names = list(COUNTRY_PROFILES.keys())
    country_texts = []
    for c in country_names:
        profile = COUNTRY_PROFILES[c]
        needs = _parse_list(profile.get("priority_needs", []))
        desc = COUNTRY_NEED_DESCRIPTIONS.get(c, "")
        country_texts.append(" ".join(needs) + " " + desc + " " + profile.get("context", ""))

    # Build policy texts
    policy_texts = []
    for p in test_policies:
        tags_str = " ".join(p.get("tags", []))
        content = p.get("content", "") or ""
        policy_texts.append(f"{p['title']} {tags_str} {content[:500]}")

    # Fit TF-IDF on combined corpus
    all_texts = country_texts + policy_texts
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    country_vecs = tfidf_matrix[:len(country_names)]
    policy_vecs = tfidf_matrix[len(country_names):]

    all_scores = []
    sector_scores = {"AI Governance": [], "Cybersecurity": [], "Data Privacy": []}

    for i, p in enumerate(test_policies):
        p_vec = policy_vecs[i]
        sims = cosine_similarity(p_vec, country_vecs).flatten()

        # Rank countries, skip self-country
        ranked = []
        for j, c in enumerate(country_names):
            if c == p["country"]:
                continue
            ranked.append((c, float(sims[j])))
        ranked.sort(key=lambda x: -x[1])

        for c, score in ranked[:5]:
            all_scores.append(score)
            sector_scores[p["sector"]].append(score)

    mean_s = np.mean(all_scores)
    std_s = np.std(all_scores)
    sec_means = [np.mean(v) for v in sector_scores.values() if v]
    bias = np.std(sec_means)
    return mean_s, std_s, bias


# ======================================================================
# 2. PolicyIQ V2 Evaluation (with optional weight overrides)
# ======================================================================
def run_policyiq_eval(test_policies, weights=None):
    """
    Evaluate PolicyIQ V2 recommender with given weights.
    Returns (mean_score, std_score, bias).
    """
    all_scores = []
    sector_scores = {"AI Governance": [], "Cybersecurity": [], "Data Privacy": []}

    for p in test_policies:
        res = get_recommendations_v2(p["id"], top_n=5, weights=weights)
        if "error" in res:
            continue
        for rec in res["recommendations"]:
            score = rec["need_score"]
            all_scores.append(score)
            sector_scores[p["sector"]].append(score)

    mean_s = np.mean(all_scores) if all_scores else 0
    std_s = np.std(all_scores) if all_scores else 0
    sec_means = [np.mean(v) for v in sector_scores.values() if v]
    bias = np.std(sec_means) if sec_means else 0
    return mean_s, std_s, bias


# ======================================================================
# MAIN EXECUTION
# ======================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("       POLICYIQ IEEE PAPER ANALYSIS SUITE")
    print("=" * 70)

    test_policies = load_test_policies()
    print(f"Loaded {len(test_policies)} test policies across 3 sectors.\n")

    # ------------------------------------------------------------------
    # TASK 1: TF-IDF Baseline vs PolicyIQ V2
    # ------------------------------------------------------------------
    print("-" * 70)
    print("TASK 1: TF-IDF BASELINE vs POLICYIQ V2 COMPARISON")
    print("-" * 70)

    tfidf_mean, tfidf_std, tfidf_bias = run_tfidf_baseline(test_policies)
    print(f"  TF-IDF Baseline computed.")

    piq_mean, piq_std, piq_bias = run_policyiq_eval(test_policies)
    print(f"  PolicyIQ V2 computed.\n")

    # Improvement calculations
    mean_improvement = ((piq_mean - tfidf_mean) / tfidf_mean * 100) if tfidf_mean > 0 else 0
    bias_improvement = ((tfidf_bias - piq_bias) / tfidf_bias * 100) if tfidf_bias > 0 else 0

    print("  TABLE: Baseline Comparison")
    print("  " + "-" * 66)
    print(f"  {'Method':<35} | {'Mean Score':>10} | {'Std Dev':>8} | {'Bias':>8}")
    print("  " + "-" * 66)
    print(f"  {'TF-IDF Cosine Baseline':<35} | {tfidf_mean:10.4f} | {tfidf_std:8.4f} | {tfidf_bias:8.4f}")
    print(f"  {'PolicyIQ V2 (Proposed)':<35} | {piq_mean:10.4f} | {piq_std:8.4f} | {piq_bias:8.4f}")
    print("  " + "-" * 66)
    print(f"  Improvement: Mean Score +{mean_improvement:.1f}%, Bias reduction {bias_improvement:.1f}%\n")

    # ------------------------------------------------------------------
    # TASK 2: Ablation Study (Zero out each factor F1-F5)
    # ------------------------------------------------------------------
    print("-" * 70)
    print("TASK 2: ABLATION STUDY (MCDA Factor Removal)")
    print("-" * 70)

    # Baseline (full model)
    full_mean, full_std, full_bias = piq_mean, piq_std, piq_bias

    ablation_configs = {
        "Full Model (All 5 Factors)": DEFAULT_WEIGHTS.copy(),
        "w/o F1: Sector Gap": {
            "sector_gap": 0.0,
            "regulatory_maturity": 0.25,
            "semantic_need": 0.20,
            "regional_pressure": 0.12,
            "economic_tier": 0.08
        },
        "w/o F2: Reg. Maturity": {
            "sector_gap": 0.35,
            "regulatory_maturity": 0.0,
            "semantic_need": 0.20,
            "regional_pressure": 0.12,
            "economic_tier": 0.08
        },
        "w/o F3: Semantic Need": {
            "sector_gap": 0.35,
            "regulatory_maturity": 0.25,
            "semantic_need": 0.0,
            "regional_pressure": 0.12,
            "economic_tier": 0.08
        },
        "w/o F4: Regional Pressure": {
            "sector_gap": 0.35,
            "regulatory_maturity": 0.25,
            "semantic_need": 0.20,
            "regional_pressure": 0.0,
            "economic_tier": 0.08
        },
        "w/o F5: Economic Tier": {
            "sector_gap": 0.35,
            "regulatory_maturity": 0.25,
            "semantic_need": 0.20,
            "regional_pressure": 0.12,
            "economic_tier": 0.0
        },
    }

    print(f"\n  TABLE: Ablation Study Results")
    print("  " + "-" * 72)
    print(f"  {'Configuration':<35} | {'Mean Score':>10} | {'Std Dev':>8} | {'Bias':>8} | {'Delta':>8}")
    print("  " + "-" * 72)

    for name, weights in ablation_configs.items():
        if name.startswith("Full"):
            a_mean, a_std, a_bias = full_mean, full_std, full_bias
            delta = 0.0
        else:
            a_mean, a_std, a_bias = run_policyiq_eval(test_policies, weights=weights)
            delta = a_mean - full_mean
        print(f"  {name:<35} | {a_mean:10.4f} | {a_std:8.4f} | {a_bias:8.4f} | {delta:+8.4f}")

    print("  " + "-" * 72)
    print("  Delta = change in mean score relative to full model (negative = degradation)\n")

    # ------------------------------------------------------------------
    # TASK 3: Country Profiles Table T4 (6 representative rows)
    # ------------------------------------------------------------------
    print("-" * 70)
    print("TASK 3: COUNTRY PROFILES TABLE (T4) - 6 Representative Nations")
    print("-" * 70)

    # Select 6 diverse profiles: 2 advanced, 2 emerging, 2 nascent
    selected = [
        "United States",   # advanced, North America
        "European Union",  # advanced, Europe
        "India",           # emerging, Asia
        "Brazil",          # emerging, South America
        "Nigeria",         # nascent, Africa
        "Indonesia",       # nascent, Asia
    ]

    print(f"\n  TABLE T4: Representative Country Profiles")
    print("  " + "-" * 110)
    print(f"  {'Country':<18} | {'Region':<14} | {'GDP Tier':<10} | {'Maturity':<12} | {'Existing Sectors':<30} | {'Priority Needs':<25}")
    print("  " + "-" * 110)

    for c in selected:
        p = COUNTRY_PROFILES[c]
        sectors = ", ".join(p.get("existing_sectors", [])) or "None"
        needs = ", ".join(p.get("priority_needs", [])[:3])
        print(f"  {c:<18} | {p['region']:<14} | {p['gdp_tier']:<10} | {p['regulatory_maturity']:<12} | {sectors:<30} | {needs:<25}")

    print("  " + "-" * 110)
    print(f"\n  Full profile count: {len(COUNTRY_PROFILES)} nations")
    print(f"  GDP Tier breakdown:")
    tiers = {}
    for c, p in COUNTRY_PROFILES.items():
        t = p["gdp_tier"]
        tiers[t] = tiers.get(t, 0) + 1
    for t, cnt in sorted(tiers.items()):
        print(f"    {t}: {cnt} countries")

    mat_counts = {}
    for c, p in COUNTRY_PROFILES.items():
        m = p["regulatory_maturity"]
        mat_counts[m] = mat_counts.get(m, 0) + 1
    print(f"  Maturity breakdown:")
    for m, cnt in sorted(mat_counts.items()):
        print(f"    {m}: {cnt} countries")

    print("\n" + "=" * 70)
    print("  ALL TASKS COMPLETE")
    print("=" * 70)
