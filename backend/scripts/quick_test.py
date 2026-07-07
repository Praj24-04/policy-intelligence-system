import sys
sys.path.insert(0, '.')
from app.ml.recommender_v2 import get_recommendations_v2

tests = ['aig_001', 'cyb_001', 'prv_001']
for pid in tests:
    r = get_recommendations_v2(pid, top_n=3)
    print(f"\n=== {r['source_policy']['title'][:50]} ===")
    for rec in r['recommendations']:
        print(f"  {rec['country']}: {rec['need_score']} | Breakdown: {rec['score_breakdown']}")