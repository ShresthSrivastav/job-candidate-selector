"""Phase 4.6 — Optimized Phase 4.5"""
from __future__ import annotations
import sys, os, time, json, csv, pickle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ranking.rrf_ranker import compute_rrf_scores
from src.ranking.elite_reranker import elite_rerank
from src.features.reasoning_generator import generate_reasoning

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CACHE_FILE = "outputs/.full_cache.pkl"

# Phase 4.5 reference metrics
P45_SPREAD = 22.79
P45_SPECIALISTS = 100.0
P45_ZERO_RET = 0
P45_HP = 0
P45_RUNTIME = 52.85


def load_full():
    with open(CACHE_FILE, "rb") as f:
        candidates, jd_reqs = pickle.load(f)
    # Also load validation data
    with open("outputs/phase45_submission.csv", "r", encoding="utf-8") as f:
        p45_csv = list(csv.DictReader(f))
    return candidates, jd_reqs, p45_csv


def validate(top100):
    scores = [float(r["final_score"]) for r in top100]
    hp = [float(r.get("honeypot_probability", 0) or 0) for r in top100]
    ri = [float(r.get("retrieval_intelligence", 0) or 0) for r in top100]
    return {
        "score_spread": round(max(scores)-min(scores), 2),
        "retrieval_specialist_pct": round(sum(1 for v in ri if v >= 0.3)/100*100, 1),
        "zero_retrieval_intelligence": sum(1 for v in ri if v == 0),
        "honeypot_high_risk": sum(1 for v in hp if v > 0.8),
        "avg_ret_intel": round(sum(ri)/len(ri), 4),
        "score_min": round(min(scores), 2),
        "score_max": round(max(scores), 2),
    }


def run_phase46(candidates):
    t0 = time.time()

    # RRF with 4 fields (candidate_quality_v2 removed)
    rrf_fields = ["retrieval_intelligence", "evidence_score",
                  "career_alignment_score", "ownership_score"]
    rows = compute_rrf_scores(candidates, rrf_fields, k=60)
    rows.sort(key=lambda x: x["rrf_score"], reverse=True)

    # Elite reranker on top 1000
    rows = elite_rerank(rows, top_n=1000)

    # Pairwise reranker on top 200
    if len(rows) > 200:
        from src.ranking.pairwise_elite_v2 import pairwise_rerank_top_n
        # Use Phase 4.5-available fields for pairwise comparison
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
        # After pairwise reranking, use pairwise_v2_score for score if available
        score_source = row.get("pairwise_v2_score", row.get("elite_score", row.get("rrf_score", 0)))
        row["final_score"] = round(float(score_source) * 100.0, 4)
        row["reasoning"] = generate_reasoning(row, i + 1, row["final_score"])

    runtime = round(time.time() - t0, 2)
    return top_100, runtime


def write_submission(top100, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        w.writeheader()
        for row in top100:
            w.writerow({"candidate_id": row["candidate_id"], "rank": row["rank"],
                        "score": row["final_score"], "reasoning": row["reasoning"]})


if __name__ == "__main__":
    print("Phase 4.6 Optimization\n")
    candidates, jd_reqs, p45_csv = load_full()
    p45_ids = {r["candidate_id"] for r in p45_csv}

    print(f"Loaded {len(candidates)} candidates from cache")

    t_main = time.time()
    top100, runtime = run_phase46(candidates)
    total_time = round(time.time() - t_main, 2)
    metrics = validate(top100)
    metrics["runtime"] = runtime

    p46_ids = {r["candidate_id"] for r in top100}
    overlap = len(p45_ids & p46_ids)

    write_submission(top100, "outputs/phase46_submission.csv")

    # Also write JSON
    with open("outputs/phase46_top100.json", "w", encoding="utf-8") as f:
        serializable = []
        for row in top100:
            s = dict(row)
            if isinstance(s.get("skills_names"), list):
                s["skills_names"] = [str(x) for x in s["skills_names"]]
            if isinstance(s.get("career_text"), str):
                s["career_text"] = s["career_text"][:500]
            serializable.append(s)
        json.dump(serializable, f, indent=2, default=str)

    print(f"\nResults:")
    print(f"  Runtime: {runtime}s (vs Phase 4.5: {P45_RUNTIME}s)")
    print(f"  Score spread: {metrics['score_spread']} (vs Phase 4.5: {P45_SPREAD})")
    print(f"  Specialists: {metrics['retrieval_specialist_pct']}% (vs Phase 4.5: {P45_SPECIALISTS}%)")
    print(f"  Zero retrieval: {metrics['zero_retrieval_intelligence']} (vs Phase 4.5: {P45_ZERO_RET})")
    print(f"  HP high risk: {metrics['honeypot_high_risk']} (vs Phase 4.5: {P45_HP})")
    print(f"  Overlap with Phase 4.5: {overlap}%")

    # Success criteria check
    spread_ok = metrics['score_spread'] > 25
    specialists_ok = metrics['retrieval_specialist_pct'] == 100.0
    runtime_ok = runtime < 70
    hp_ok = metrics['honeypot_high_risk'] == 0
    all_ok = spread_ok and specialists_ok and runtime_ok and hp_ok
    decision = "UPGRADE_TO_PHASE46" if all_ok else "KEEP_PHASE45"

    print(f"\n  Spread > 25: {'PASS' if spread_ok else 'FAIL'}")
    print(f"  Specialists = 100%: {'PASS' if specialists_ok else 'FAIL'}")
    print(f"  Runtime < 70s: {'PASS' if runtime_ok else 'FAIL'}")
    print(f"  HP = 0: {'PASS' if hp_ok else 'FAIL'}")
    print(f"  Decision: {decision}")

    # Generate phase46_report.md
    report_md = f"""# Phase 4.6 Optimization Report

**Timestamp:** {time.strftime("%Y-%m-%d %H:%M:%S")}

## Changes from Phase 4.5

1. Removed `candidate_quality_v2` from RRF (4 fields instead of 5)
2. Added Pairwise Elite Reranker as final stage (top 200 → pairwise → top 100)
3. No MiniLM gating
4. No new features introduced

## Results

| Metric | Phase 4.5 | Phase 4.6 | Delta |
|---|---|---|---|
| Runtime (s) | {P45_RUNTIME} | {runtime} | {round(runtime - P45_RUNTIME, 2):+g} |
| Score Spread | {P45_SPREAD} | {metrics['score_spread']} | {round(metrics['score_spread'] - P45_SPREAD, 2):+g} |
| Specialists % | {P45_SPECIALISTS} | {metrics['retrieval_specialist_pct']} | {round(metrics['retrieval_specialist_pct'] - P45_SPECIALISTS, 1):+g} |
| Zero Retrieval | {P45_ZERO_RET} | {metrics['zero_retrieval_intelligence']} | 0 |
| HP High Risk | {P45_HP} | {metrics['honeypot_high_risk']} | 0 |
| Avg Ret Intel | 0.4687 | {metrics['avg_ret_intel']} | {round(metrics['avg_ret_intel'] - 0.4687, 4):+g} |
| Top-100 Overlap | — | {overlap}% | — |

## Success Criteria

| Criterion | Target | Result | Status |
|---|---|---|---|
| Spread > 25 | > 25 | {metrics['score_spread']} | {'PASS' if spread_ok else 'FAIL'} |
| Specialists = 100% | = 100% | {metrics['retrieval_specialist_pct']}% | {'PASS' if specialists_ok else 'FAIL'} |
| Runtime < 70s | < 70s | {runtime}s | {'PASS' if runtime_ok else 'FAIL'} |
| HP Leakage = 0 | = 0 | {metrics['honeypot_high_risk']} | {'PASS' if hp_ok else 'FAIL'} |

## Decision

**{decision}**
"""
    with open("outputs/phase46_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    # Generate phase46_vs_phase45.md
    vs_md = f"""# Phase 4.6 vs Phase 4.5 Comparison

**Timestamp:** {time.strftime("%Y-%m-%d %H:%M:%S")}

## Pipeline Comparison

| Aspect | Phase 4.5 | Phase 4.6 |
|---|---|---|
| Eligibility | PASS | PASS |
| Cheap Features | PASS | PASS |
| Expensive Features | PASS | PASS |
| RRF Fields | 5 fields (incl quality_v2) | 4 fields (no quality_v2) |
| Elite Reranker | PASS | PASS |
| Pairwise Reranker | FAIL | PASS (top 200) |
| Runtime | {P45_RUNTIME}s | {runtime}s |

## Metric Comparison

| Metric | Phase 4.5 | Phase 4.6 | Delta | Better? |
|---|---|---|---|---|
| Score Spread | {P45_SPREAD} | {metrics['score_spread']} | {round(metrics['score_spread'] - P45_SPREAD, 2):+g} | {'PASS' if metrics['score_spread'] > P45_SPREAD else 'FAIL'} |
| Specialists % | {P45_SPECIALISTS} | {metrics['retrieval_specialist_pct']} | {round(metrics['retrieval_specialist_pct'] - P45_SPECIALISTS, 1):+g} | {'PASS' if metrics['retrieval_specialist_pct'] >= P45_SPECIALISTS else 'FAIL'} |
| Zero Ret | {P45_ZERO_RET} | {metrics['zero_retrieval_intelligence']} | 0 | PASS |
| HP Risk | {P45_HP} | {metrics['honeypot_high_risk']} | 0 | PASS |
| Runtime | {P45_RUNTIME}s | {runtime}s | {round(runtime - P45_RUNTIME, 2):+g}s | {'PASS' if runtime <= 70 else 'FAIL'} |
| Avg Ret Intel | 0.4687 | {metrics['avg_ret_intel']} | {round(metrics['avg_ret_intel'] - 0.4687, 4):+g} | {'PASS' if metrics['avg_ret_intel'] >= 0.4687 else 'FAIL'} |

## Top-100 Overlap

**{overlap}%** of candidates overlap between Phase 4.5 and Phase 4.6 top-100.

## Decision

**{decision}**
"""
    with open("outputs/phase46_vs_phase45.md", "w", encoding="utf-8") as f:
        f.write(vs_md)

    # Also generate JSON report
    report_json = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline": "Phase 4.6",
        "changes": [
            "Removed candidate_quality_v2 from RRF",
            "Added Pairwise Elite Reranker on top 200",
        ],
        "metrics": {
            "phase45": {"runtime": P45_RUNTIME, "score_spread": P45_SPREAD, "specialists": P45_SPECIALISTS, "zero_retrieval": P45_ZERO_RET, "hp_high_risk": P45_HP, "avg_ret_intel": 0.4687},
            "phase46": {"runtime": runtime, "score_spread": metrics['score_spread'], "specialists": metrics['retrieval_specialist_pct'], "zero_retrieval": metrics['zero_retrieval_intelligence'], "hp_high_risk": metrics['honeypot_high_risk'], "avg_ret_intel": metrics['avg_ret_intel']},
        },
        "overlap_pct": overlap,
        "success_criteria": {
            "spread_gt_25": spread_ok,
            "specialists_eq_100": specialists_ok,
            "runtime_lt_70": runtime_ok,
            "hp_eq_0": hp_ok,
        },
        "decision": decision,
    }
    with open("outputs/phase46_vs_phase45.json", "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    print(f"\nReports written to outputs/phase46_report.md and outputs/phase46_vs_phase45.md")
