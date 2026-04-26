import sys
sys.path.insert(0, '.')
from app.services.recommender import get_recommendations, _ensure_trained

_ensure_trained()

tests = ['aig_001', 'cyb_001', 'prv_001']
for pid in tests:
    r = get_recommendations(pid, top_n=3)
    print(f"\n=== {r['source_policy']['title'][:50]} ===")
    for rec in r['recommendations']:
        print(f"  {rec['country']}: {rec['need_score']}")