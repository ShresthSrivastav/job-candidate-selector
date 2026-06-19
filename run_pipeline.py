"""Single entry point for the RedRobe candidate ranking pipeline.
Usage:
    python run_pipeline.py
    python run_pipeline.py --candidates Data/candidates.jsonl --jd Data/job_description.txt
"""
from __future__ import annotations
import sys, os, time, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.phase45_pipeline import phase45_pipeline
from scripts.phase46_optimization import run_phase46, validate, write_submission, load_full
from scripts.phase46_release_freeze import validate_submission


DEFAULT_CANDIDATES = "Data/candidates.jsonl"
DEFAULT_JD = "Data/job_description.txt"
OUTPUT_DIR = "outputs"


def parse_args():
    parser = argparse.ArgumentParser(description="RedRobe Candidate Ranking Pipeline")
    parser.add_argument("--candidates", default=DEFAULT_CANDIDATES, help="Path to candidates JSONL")
    parser.add_argument("--jd", default=DEFAULT_JD, help="Path to job description text file")
    parser.add_argument("--stage2_k", type=int, default=20000, help="Prefilter top-K by cheap score")
    parser.add_argument("--skip-phase45", action="store_true", help="Skip Phase 4.5 if cache exists")
    parser.add_argument("--skip-release", action="store_true", help="Skip release freeze")
    return parser.parse_args()


def main():
    args = parse_args()
    t_start = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not args.skip_phase45:
        print("=" * 60)
        print("Phase 4.5: Feature Computation Pipeline")
        print("=" * 60)
        t0 = time.time()
        rows = phase45_pipeline(
            candidates_path=args.candidates,
            jd_path=args.jd,
            submission_path="outputs/phase45_submission.csv",
            output_json_path="outputs/phase45_top100.json",
            stage2_k=args.stage2_k,
        )
        print(f"Phase 4.5 complete: {len(rows)} rows in {time.time() - t0:.2f}s")
    else:
        print("Skipping Phase 4.5 (--skip-phase45)")

    print()
    print("=" * 60)
    print("Phase 4.6: Optimized Ranking")
    print("=" * 60)
    t0 = time.time()
    candidates, jd_reqs, p45_csv = load_full()
    print(f"Loaded {len(candidates)} candidates from cache")
    top100, runtime = run_phase46(candidates)
    metrics = validate(top100)
    metrics["runtime"] = runtime
    write_submission(top100, "outputs/phase46_submission.csv")

    p46_ids = {r["candidate_id"] for r in top100}
    p45_ids = {r["candidate_id"] for r in p45_csv}
    overlap = len(p45_ids & p46_ids)
    print(f"Phase 4.6 complete: {time.time() - t0:.2f}s")
    print(f"  Runtime: {runtime}s")
    print(f"  Score spread: {metrics['score_spread']}")
    print(f"  Specialists: {metrics['retrieval_specialist_pct']}%")
    print(f"  Zero retrieval: {metrics['zero_retrieval_intelligence']}")
    print(f"  HP high risk: {metrics['honeypot_high_risk']}")
    print(f"  Avg ret intel: {metrics['avg_ret_intel']}")
    print(f"  Overlap with Phase 4.5: {overlap}%")

    if not args.skip_release:
        print()
        print("=" * 60)
        print("Release Freeze")
        print("=" * 60)
        t0 = time.time()
        import subprocess
        result = subprocess.run([sys.executable, "scripts/phase46_release_freeze.py"],
                                capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        print(result.stdout)
        if result.returncode != 0:
            print(f"Release freeze failed: {result.stderr}")
            sys.exit(1)
        print(f"Release freeze complete: {time.time() - t0:.2f}s")
    else:
        print("Skipping release freeze (--skip-release)")

    total_time = time.time() - t_start
    print()
    print("=" * 60)
    print(f"Pipeline complete in {total_time:.2f}s")
    print("=" * 60)
    print(f"Outputs:")
    print(f"  outputs/phase46_submission.csv")
    print(f"  outputs/phase46_top100.json")
    print(f"  outputs/phase46_report.md")
    print(f"  outputs/phase46_vs_phase45.md")
    print(f"  outputs/phase46_submission_audit.md")
    print(f"  release_v110/ (after freeze)")


if __name__ == "__main__":
    main()
