import sys
sys.path.insert(0, '.')

from app.services.recommender import get_recommendations, _ensure_trained
import numpy as np

_ensure_trained()

all_policy_ids = [
    # AI Governance
    "aig_001", "aig_002", "aig_003", "aig_004", "aig_005",
    "aig_006", "aig_007", "aig_008", "aig_009", "aig_010",
    # Cybersecurity
    "cyb_001", "cyb_002", "cyb_003", "cyb_004", "cyb_005",
    "cyb_006", "cyb_007", "cyb_008", "cyb_009", "cyb_010",
    # Data Privacy
    "prv_001", "prv_002", "prv_003", "prv_004", "prv_005",
    "prv_006", "prv_007", "prv_008", "prv_009", "prv_010",
]

print("\n" + "="*60)
print("MODEL EVALUATION REPORT")
print("="*60)

# ── 1. Score Distribution Analysis ──────────────────────────
all_scores = []
sector_scores = {"AI Governance": [], "Cybersecurity": [], "Data Privacy": []}
country_frequency = {}

for pid in all_policy_ids:
    result = get_recommendations(pid, top_n=6)
    sector = result["source_policy"]["sector"]
    
    for rec in result["recommendations"]:
        score = rec["need_score"]
        all_scores.append(score)
        sector_scores[sector].append(score)
        
        country = rec["country"]
        if country not in country_frequency:
            country_frequency[country] = 0
        country_frequency[country] += 1

print("\n📊 SCORE DISTRIBUTION (all policies):")
print(f"  Mean score:    {np.mean(all_scores):.3f}")
print(f"  Std deviation: {np.std(all_scores):.3f}  ← higher = more varied = better")
print(f"  Min score:     {np.min(all_scores):.3f}")
print(f"  Max score:     {np.max(all_scores):.3f}")
print(f"  Range:         {np.max(all_scores) - np.min(all_scores):.3f}")

# ── 2. Bias Check ────────────────────────────────────────────
print("\n🎯 BIAS CHECK (per sector mean scores):")
for sector, scores in sector_scores.items():
    print(f"  {sector}: mean={np.mean(scores):.3f}, std={np.std(scores):.3f}")

sector_means = [np.mean(s) for s in sector_scores.values()]
bias = np.std(sector_means)
print(f"\n  Inter-sector bias: {bias:.3f}")
if bias < 0.05:
    print("  ✅ LOW BIAS — sectors treated fairly")
elif bias < 0.15:
    print("  ⚠️  MODERATE BIAS — slight sector preference")
else:
    print("  ❌ HIGH BIAS — model favors certain sectors")

# ── 3. Variance Check ────────────────────────────────────────
print("\n📈 VARIANCE CHECK:")
policy_top_countries = {}
for pid in all_policy_ids:
    result = get_recommendations(pid, top_n=3)
    top3 = [r["country"] for r in result["recommendations"]]
    policy_top_countries[pid] = top3

# Check how many unique top-1 countries exist
top1_countries = [policy_top_countries[pid][0] for pid in all_policy_ids]
unique_top1 = len(set(top1_countries))
print(f"  Unique #1 recommended countries: {unique_top1} / {len(all_policy_ids)} policies")

if unique_top1 <= 3:
    print("  ❌ HIGH VARIANCE ISSUE — same countries dominate all recommendations")
elif unique_top1 <= 8:
    print("  ⚠️  MODERATE — some variety but limited")
else:
    print("  ✅ GOOD VARIETY — different countries recommended for different policies")

# ── 4. Country Frequency (Dominance Check) ───────────────────
print("\n🌍 COUNTRY RECOMMENDATION FREQUENCY (out of 30 policies × 6 recs = 180 slots):")
sorted_freq = sorted(country_frequency.items(), key=lambda x: -x[1])
for country, freq in sorted_freq[:10]:
    bar = "█" * freq
    pct = freq / 180 * 100
    flag = "❌ DOMINANT" if pct > 20 else "⚠️" if pct > 12 else "✅"
    print(f"  {country:<25} {freq:>3}x ({pct:.1f}%) {bar} {flag}")

# ── 5. Cross-sector Differentiation ─────────────────────────
print("\n🔄 CROSS-SECTOR DIFFERENTIATION:")
ai_top = set()
cyber_top = set()
priv_top = set()

for pid in all_policy_ids:
    result = get_recommendations(pid, top_n=3)
    sector = result["source_policy"]["sector"]
    countries = set(r["country"] for r in result["recommendations"])
    
    if sector == "AI Governance":
        ai_top.update(countries)
    elif sector == "Cybersecurity":
        cyber_top.update(countries)
    elif sector == "Data Privacy":
        priv_top.update(countries)

ai_cyber_overlap = len(ai_top & cyber_top) / len(ai_top | cyber_top)
ai_priv_overlap = len(ai_top & priv_top) / len(ai_top | priv_top)
cyber_priv_overlap = len(cyber_top & priv_top) / len(cyber_top | priv_top)

print(f"  AI Governance ↔ Cybersecurity overlap: {ai_cyber_overlap:.2f}  (lower = more differentiated)")
print(f"  AI Governance ↔ Data Privacy overlap:  {ai_priv_overlap:.2f}")
print(f"  Cybersecurity ↔ Data Privacy overlap:  {cyber_priv_overlap:.2f}")

avg_overlap = np.mean([ai_cyber_overlap, ai_priv_overlap, cyber_priv_overlap])
if avg_overlap < 0.4:
    print(f"\n  ✅ GOOD DIFFERENTIATION — sectors recommend different countries (avg overlap: {avg_overlap:.2f})")
elif avg_overlap < 0.6:
    print(f"\n  ⚠️  MODERATE — some cross-sector similarity (avg overlap: {avg_overlap:.2f})")
else:
    print(f"\n  ❌ POOR DIFFERENTIATION — sectors too similar (avg overlap: {avg_overlap:.2f})")

# ── 6. Final Verdict ─────────────────────────────────────────
print("\n" + "="*60)
print("FINAL VERDICT")
print("="*60)
score_std = np.std(all_scores)
if score_std > 0.08 and unique_top1 > 6 and avg_overlap < 0.6:
    print("✅ MODEL IS WORKING WELL")
    print("   Good score variation, country diversity, sector differentiation")
elif score_std > 0.05 and unique_top1 > 4:
    print("⚠️  MODEL IS ACCEPTABLE")
    print("   Some variation exists but could be improved")
else:
    print("❌ MODEL HAS ISSUES")
    print("   Scores too uniform or countries too repetitive")
print("="*60)