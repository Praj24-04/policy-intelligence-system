"""
Paper Analysis Part 2: API Latency + Temporal Scope
"""
import sys, time
from pathlib import Path
import numpy as np

_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection

# ======================================================================
# TASK 1: Temporal Scope of Corpus
# ======================================================================
print("=" * 70)
print("TASK A: TEMPORAL SCOPE OF POLICY CORPUS")
print("=" * 70)

conn = get_connection()

# Year distribution
rows = conn.execute("SELECT year, COUNT(*) as cnt FROM policies WHERE year IS NOT NULL GROUP BY year ORDER BY year").fetchall()
print("\nYear distribution:")
total_with_year = 0
for r in rows:
    total_with_year += r["cnt"]
    print(f"  {r['year']}: {r['cnt']} policies")

null_year = conn.execute("SELECT COUNT(*) as cnt FROM policies WHERE year IS NULL").fetchone()["cnt"]
total = conn.execute("SELECT COUNT(*) as cnt FROM policies").fetchone()["cnt"]
print(f"\n  Policies with year: {total_with_year}")
print(f"  Policies without year: {null_year}")
print(f"  Total: {total}")

# Check for timestamp columns (may not exist)
for col in ["created_at", "updated_at"]:
    try:
        ts = conn.execute(f"SELECT MIN({col}) as min_dt, MAX({col}) as max_dt FROM policies WHERE {col} IS NOT NULL").fetchone()
        if ts and ts["min_dt"]:
            print(f"\n  {col} range:")
            print(f"    Earliest: {ts['min_dt']}")
            print(f"    Latest:   {ts['max_dt']}")
    except Exception:
        print(f"\n  Column '{col}' not present in schema (temporal scope derived from year field).")
        conn = get_connection()  # reconnect after error

# Derive temporal scope summary from year
if rows:
    min_year = rows[0]["year"]
    max_year = rows[-1]["year"]
    print(f"\n  TEMPORAL SCOPE SUMMARY:")
    print(f"    Policy publication range: {min_year} - {max_year}")
    print(f"    Span: {max_year - min_year} years")
    # Count policies in last 5 years
    recent = sum(r["cnt"] for r in rows if r["year"] >= 2021)
    print(f"    Policies from 2021-2026 (recent): {recent} ({recent/total*100:.1f}%)")
    legacy = sum(r["cnt"] for r in rows if r["year"] < 2021)
    print(f"    Policies pre-2021 (legacy): {legacy} ({legacy/total*100:.1f}%)")

conn.close()

# ======================================================================
# TASK 2: API Latency Benchmarks (T8)
# ======================================================================
print("\n" + "=" * 70)
print("TASK B: API LATENCY BENCHMARKS (for Table T8)")
print("=" * 70)

from app.ml.recommender_v2 import get_recommendations_v2

# Get sample policy IDs across sectors
conn = get_connection()
samples = conn.execute("""
    SELECT id, sector FROM policies
    WHERE embedding IS NOT NULL
      AND sector IN ('AI Governance', 'Cybersecurity', 'Data Privacy')
    ORDER BY sector, id
""").fetchall()
conn.close()

by_sector = {}
for s in samples:
    sec = s["sector"]
    if sec not in by_sector:
        by_sector[sec] = []
    if len(by_sector[sec]) < 5:
        by_sector[sec].append(s["id"])

test_ids = []
for sec in ["AI Governance", "Cybersecurity", "Data Privacy"]:
    test_ids.extend(by_sector.get(sec, []))

# Warm-up run (first call loads models, caches, etc.)
print("\n  Warm-up run (discarded)...")
_ = get_recommendations_v2(test_ids[0], top_n=5)

# Benchmark runs
latencies_by_topn = {}
for top_n in [3, 5, 10]:
    times = []
    for pid in test_ids:
        start = time.perf_counter()
        res = get_recommendations_v2(pid, top_n=top_n)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # convert to ms
    latencies_by_topn[top_n] = times

print(f"\n  Benchmarked {len(test_ids)} policies x 3 top_n settings\n")

print("  TABLE T8: /recommend API Latency (ms)")
print("  " + "-" * 60)
print(f"  {'top_n':<8} | {'Mean (ms)':>10} | {'Median':>10} | {'P95':>10} | {'Max':>10}")
print("  " + "-" * 60)
for top_n, times in latencies_by_topn.items():
    mean_t = np.mean(times)
    med_t = np.median(times)
    p95_t = np.percentile(times, 95)
    max_t = np.max(times)
    print(f"  {top_n:<8} | {mean_t:10.1f} | {med_t:10.1f} | {p95_t:10.1f} | {max_t:10.1f}")
print("  " + "-" * 60)

# Also time the /compare endpoint equivalent
print("\n  Timing /compare equivalent (comparator_v2)...")
try:
    from app.ml.comparator_v2 import compare_policies_v2
    compare_ids = test_ids[:6]  # pick 3 pairs
    compare_times = []
    for i in range(0, len(compare_ids) - 1, 2):
        start = time.perf_counter()
        _ = compare_policies_v2(compare_ids[i], compare_ids[i+1])
        elapsed = time.perf_counter() - start
        compare_times.append(elapsed * 1000)
    print(f"  /compare latency: mean={np.mean(compare_times):.1f}ms, median={np.median(compare_times):.1f}ms")
except Exception as e:
    print(f"  /compare benchmark skipped: {e}")

print("\n" + "=" * 70)
print("  TASKS A & B COMPLETE")
print("=" * 70)
