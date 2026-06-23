"""Prefilter Impact Audit — Compare K values for stage2 cheap-filter.
Runs Phase 4.5 with K=100000 to capture all eligible candidates,
then simulates K=100000, 50000, 20000, 10000 by slicing and running Phase 4.6 ranking.
"""
from __future__ import annotations
import sys
import os
import time
import json
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ranking.rrf_ranker import compute_rrf_scores
from src.ranking.elite_reranker import elite_rerank

# Also import Phase 4.5 pipeline to regenerate cache
from scripts.phase45_pipeline import phase45_pipeline
from src.parser.jd_parser import JDParser

CANDIDATES_PATH = "Data/candidates.jsonl"
JD_PATH = "Data/job_description.txt"
OUTPUT_DIR = "outputs"

# Step 1: Run Phase 4.5 with K=100000 to capture ALL eligible candidates
print("=" * 70)
print("PRE-FILTER IMPACT AUDIT — Phase 4.5 with K=100000 (all eligible)")
print("=" * 70)

FULL_CACHE = "outputs/.full_eligible_cache.pkl"

if not os.path.exists(FULL_CACHE):
    t0 = time.time()
    all_rows = phase45_pipeline(
        candidates_path=CANDIDATES_PATH,
        jd_path=JD_PATH,
        submission_path="outputs/audit_phase45_k100000.csv",
        output_json_path="outputs/audit_phase45_k100000.json",
        batch_size=10000,
        eligibility_threshold=0.25,
        stage2_k=100000,  # effectively no filter
    )
    print(f"Phase 4.5 K=100000 completed in {time.time() - t0:.2f}s")
    print(f"Total rows in stage2b output: {len(all_rows)}")

    # Save cache (we only need rows, not jd_reqs for ranking)
    with open(FULL_CACHE, "wb") as f:
        pickle.dump(all_rows, f)
else:
    print(f"Loading cached full eligible set from {FULL_CACHE}")
    with open(FULL_CACHE, "rb") as f:
        all_rows = pickle.load(f)
    print(f"Loaded {len(all_rows)} rows")

# Also load jd_reqs for consistency
jd_parser = JDParser()
with open(JD_PATH, "r", encoding="utf-8") as f:
    jd_text = f.read()
jd_reqs = jd_parser.parse(jd_text)

# Step 2: Define Phase 4.6 ranking function
def run_ranking(candidates_subset, label=""):
    """Run Phase 4.6 ranking on a subset of candidates."""
    t0 = time.time()

    rrf_fields = ["retrieval_intelligence", "evidence_score",
                  "career_alignment_score", "ownership_score"]
    rows = compute_rrf_scores(candidates_subset, rrf_fields, k=60)
    rows.sort(key=lambda x: x["rrf_score"], reverse=True)

    rows = elite_rerank(rows, top_n=1000)

    if len(rows) > 200:
        from src.ranking.pairwise_elite_v2 import pairwise_rerank_top_n
        pairwise_fields = [
            ("retrieval_intelligence", 1.5),
            ("ownership_score", 1.2),
            ("evidence_score", 1.0),
            ("career_alignment_score", 0.8),
            ("jd_coverage", 0.5),
        ]
        import src.ranking.pairwise_elite_v2 as pw
        pw.COMPARISON_FIELDS = pairwise_fields
        rows = pairwise_rerank_top_n(rows, top_n=200, keep_rest=False)

    top_100 = rows[:100]
    for i, row in enumerate(top_100):
        row["rank"] = i + 1
        score_source = row.get("pairwise_v2_score", row.get("elite_score", row.get("rrf_score", 0)))
        row["final_score"] = round(float(score_source) * 100.0, 4)

    runtime = round(time.time() - t0, 2)

    # Metrics
    scores = [float(r["final_score"]) for r in top_100]
    ri = [float(r.get("retrieval_intelligence", 0) or 0) for r in top_100]
    hp = [float(r.get("honeypot_probability", 0) or 0) for r in top_100]

    metrics = {
        "runtime": runtime,
        "score_spread": round(max(scores) - min(scores), 2),
        "retrieval_specialist_pct": round(sum(1 for v in ri if v >= 0.3) / 100 * 100, 1),
        "zero_retrieval_intelligence": sum(1 for v in ri if v == 0),
        "honeypot_high_risk": sum(1 for v in hp if v > 0.8),
        "avg_ret_intel": round(sum(ri) / len(ri), 4),
        "score_min": round(min(scores), 2),
        "score_max": round(max(scores), 2),
    }

    ids = [r["candidate_id"] for r in top_100]
    return top_100, metrics, set(ids)


# Step 3: Run for each K value
K_VALUES = [100000, 50000, 20000, 10000]
results = {}

# Sort all rows by cheap score descending (should already be sorted from Phase 4.5)
all_rows_sorted = sorted(all_rows, key=lambda x: x.get("_cheap_score", 0), reverse=True)
print(f"\nTotal eligible candidates: {len(all_rows_sorted)}")
print(f"Cheap score range: {all_rows_sorted[0].get('_cheap_score', 0):.4f} - {all_rows_sorted[-1].get('_cheap_score', 0):.4f}")

for k in K_VALUES:
    effective_k = min(k, len(all_rows_sorted))
    subset = all_rows_sorted[:effective_k]
    print(f"\n{'=' * 50}")
    print(f"K={k} (effective={effective_k})")

    top100, metrics, ids = run_ranking(subset, label=f"K={k}")
    results[k] = {
        "effective_k": effective_k,
        "top100": top100,
        "metrics": metrics,
        "ids": ids,
    }

    print(f"  Runtime: {metrics['runtime']}s")
    print(f"  Score spread: {metrics['score_spread']}")
    print(f"  Specialists: {metrics['retrieval_specialist_pct']}%")
    print(f"  Zero retrieval: {metrics['zero_retrieval_intelligence']}")
    print(f"  HP high risk: {metrics['honeypot_high_risk']}")
    print(f"  Avg ret intel: {metrics['avg_ret_intel']}")
    print(f"  Score range: {metrics['score_min']} - {metrics['score_max']}")
    print(f"  Top 100 IDs: {ids}")


# Step 4: Compare top-100 sets
baseline = results[100000]
print(f"\n{'=' * 70}")
print("TOP-100 OVERLAP ANALYSIS (vs K=100000 baseline)")
print("=" * 70)

overlap_data = {}
for k in [50000, 20000, 10000]:
    overlap_count = len(baseline["ids"] & results[k]["ids"])
    overlap_pct = round(overlap_count / 100 * 100, 1)
    missing_ids = baseline["ids"] - results[k]["ids"]
    extra_ids = results[k]["ids"] - baseline["ids"]

    overlap_data[k] = {
        "overlap_count": overlap_count,
        "overlap_pct": overlap_pct,
        "missing_from_baseline": sorted(list(missing_ids)),
        "extra_not_in_baseline": sorted(list(extra_ids)),
    }

    print(f"\nK={k}:")
    print(f"  Overlap with K=100000: {overlap_count}/100 ({overlap_pct}%)")
    if missing_ids:
        print(f"  Candidates in K=100000 top100 but NOT in K={k} top100:")
        for cid in sorted(missing_ids):
            print(f"    - {cid}")
    else:
        print("  No candidates lost from K=100000 top100")

    if extra_ids:
        print(f"  Candidates in K={k} top100 but NOT in K=100000 top100:")
        for cid in sorted(extra_ids):
            print(f"    - {cid}")

# Step 5: For missing candidates, explain why they were filtered
print(f"\n{'=' * 70}")
print("ROOT CAUSE: Why were candidates removed by prefilter?")
print("=" * 70)

for k in [20000]:
    missing = overlap_data[k]["missing_from_baseline"]
    if not missing:
        print(f"  No candidates removed by K={k} prefilter from final Top100.")
        print("  The prefilter does NOT remove any would-be Top100 candidates.")
    else:
        print(f"  {len(missing)} candidates removed by K={k} prefilter:")
        for cid in missing:
            # Find the candidate in the full data
            idx = None
            for i, r in enumerate(all_rows_sorted):
                if r.get("candidate_id") == cid:
                    idx = i
                    cheap = r.get("_cheap_score", 0)
                    break
            print(f"    {cid}: cheap_score={cheap:.4f}, rank_by_cheap={idx}/{len(all_rows_sorted)}")


# Step 6: Write audit reports
print(f"\n{'=' * 70}")
print("WRITING REPORTS")
print("=" * 70)

# Determine recommendation
current_k = 20000
missing_current = overlap_data[current_k]["missing_from_baseline"]
if len(missing_current) == 0:
    recommendation = "KEEP_PREFILTER"
    recommendation_reason = "The current prefilter (K=20000) does not remove any candidates that would reach the final Top100 when ranking the full 100k dataset."
elif len(missing_current) <= 5:
    recommendation = "REDESIGN_PREFILTER"
    recommendation_reason = f"The current prefilter (K=20000) removes {len(missing_current)} candidates from the final Top100. Consider relaxing the threshold or adding a catch mechanism."
else:
    recommendation = "REMOVE_PREFILTER"
    recommendation_reason = f"The current prefilter (K=20000) removes {len(missing_current)} candidates from the final Top100. The prefilter is too aggressive and should be removed."

# Build markdown report
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
total_eligible = len(all_rows_sorted)

rows_md = []
for k in K_VALUES:
    m = results[k]["metrics"]
    od = overlap_data[k] if k != 100000 else {"overlap_count": 100, "overlap_pct": 100.0}
    rows_md.append(f"| {k} | {results[k]['effective_k']} | {m['runtime']} | {od['overlap_pct']}% | {m['retrieval_specialist_pct']}% | {m['zero_retrieval_intelligence']} | {m['score_spread']} | {m['avg_ret_intel']} |")

missing_list_md = ""
if missing_current:
    missing_list_md = "\n### Candidates Removed by K=20000 Prefilter\n\n| Candidate ID | Cheap Score | Cheap Rank / Total |\n|---|---|---|\n"
    for cid in missing_current:
        for i, r in enumerate(all_rows_sorted):
            if r.get("candidate_id") == cid:
                cheap = r.get("_cheap_score", 0)
                missing_list_md += f"| {cid} | {cheap:.4f} | {i}/{total_eligible} |\n"
                break
else:
    missing_list_md = "\n**No candidates were removed by the current prefilter (K=20000).**\n"

report_md = f"""# Prefilter Impact Audit

**Generated:** {timestamp}

## Purpose

Evaluate the impact of the `stage2_k` cheap-score prefilter on final Top100 quality.
The prefilter runs after cheap feature computation and keeps the top-K candidates
by cheap score before expensive features are computed.

## Methodology

1. Ran Phase 4.5 pipeline with `stage2_k=100000` (effectively disabled) to capture all eligible candidates with cheap + expensive features
2. Identified **{total_eligible}** total eligible candidates after eligibility filter
3. For each K value, simulated the prefilter by slicing to top-K by cheap score
4. Applied Phase 4.6 ranking (RRF + Elite + Pairwise) to each subset
5. Compared Top100 sets against baseline (K=100000)

## Results

### K Comparison Table

| K | Effective K | Runtime (s) | Top100 Overlap | Specialists % | Zero Retrieval | Score Spread | Avg Ret Intel |
|---|---|---|---|---|---|---|---|
{''.join(rows_md)}

### Key Differences

| K | Overlap with Baseline | Missing from Baseline |
|---|---|---|
| 50000 | {overlap_data[50000]['overlap_pct']}% ({overlap_data[50000]['overlap_count']}/100) | {len(overlap_data[50000]['missing_from_baseline'])} |
| 20000 | {overlap_data[20000]['overlap_pct']}% ({overlap_data[20000]['overlap_count']}/100) | {len(overlap_data[20000]['missing_from_baseline'])} |
| 10000 | {overlap_data[10000]['overlap_pct']}% ({overlap_data[10000]['overlap_count']}/100) | {len(overlap_data[10000]['missing_from_baseline'])} |

{missing_list_md}

## Answer

### Does the current prefilter (K=20000) remove any candidates that would enter the final Top100 when ranking the full 100k dataset?

**{'YES' if missing_current else 'NO'}**

{recommendation_reason}

## Recommendation

**{recommendation}**

{recommendation_reason}
"""

with open("outputs/prefilter_impact_audit.md", "w", encoding="utf-8") as f:
    f.write(report_md)

# Build JSON report
report_json = {
    "audit": "prefilter_impact_audit",
    "timestamp": timestamp,
    "total_eligible_candidates": total_eligible,
    "baseline_k": 100000,
    "results": {},
    "overlap_analysis": {},
    "current_prefilter_k": 20000,
    "prefilter_removes_top100_candidates": len(missing_current) > 0,
    "candidates_removed_count": len(missing_current),
    "candidates_removed": overlap_data[20000]["missing_from_baseline"],
    "recommendation": recommendation,
    "recommendation_reason": recommendation_reason,
}

for k in K_VALUES:
    m = results[k]["metrics"]
    report_json["results"][str(k)] = {
        "effective_k": results[k]["effective_k"],
        "runtime_seconds": m["runtime"],
        "score_spread": m["score_spread"],
        "retrieval_specialist_pct": m["retrieval_specialist_pct"],
        "zero_retrieval_intelligence": m["zero_retrieval_intelligence"],
        "honeypot_high_risk": m["honeypot_high_risk"],
        "avg_ret_intel": m["avg_ret_intel"],
        "score_min": m["score_min"],
        "score_max": m["score_max"],
    }
    if k != 100000:
        report_json["overlap_analysis"][str(k)] = {
            "overlap_with_baseline_count": overlap_data[k]["overlap_count"],
            "overlap_with_baseline_pct": overlap_data[k]["overlap_pct"],
            "missing_from_baseline": overlap_data[k]["missing_from_baseline"],
            "extra_not_in_baseline": overlap_data[k]["extra_not_in_baseline"],
        }

with open("outputs/prefilter_impact_audit.json", "w", encoding="utf-8") as f:
    json.dump(report_json, f, indent=2)

print(f"\n{'=' * 70}")
print("AUDIT COMPLETE")
print(f"{'=' * 70}")
print(f"  Total eligible candidates: {total_eligible}")
print(f"  Prefilter removes Top100 candidates: {'YES' if missing_current else 'NO'}")
if missing_current:
    print(f"  Candidates removed: {len(missing_current)}")
    for cid in missing_current:
        print(f"    - {cid}")
print(f"  Recommendation: {recommendation}")
print("\n  Reports written:")
print("    outputs/prefilter_impact_audit.md")
print("    outputs/prefilter_impact_audit.json")
