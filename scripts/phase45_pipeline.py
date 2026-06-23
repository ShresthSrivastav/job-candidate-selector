from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import time
import csv
import json
from typing import Dict, Any, List

from src.utils.logger import info, warning
from src.ingestion.load_candidates import stream_jsonl
from src.parser.jd_parser import JDParser
from src.parser.candidate_parser import normalize_candidate
from src.features.behavior_features import compute_behavioral_features
from src.features.reasoning_generator import generate_reasoning
from src.features.eligibility_features import compute_eligibility
from src.features.retrieval_depth_features import compute_retrieval_depth
from src.features.retrieval_maturity_features import compute_retrieval_maturity
from src.features.retrieval_specialist_classifier import compute_retrieval_specialist_probability
from src.features.impact_features import compute_impact_score
from src.features.retrieval_intelligence import compute_retrieval_intelligence
from src.features.career_alignment_features import compute_career_alignment
from src.features.ownership_features import compute_ownership_score
from src.features.risk_features import compute_risk_score
from src.features.candidate_quality_v2 import compute_quality_v2
from src.features.evidence_features import extract_evidence
from src.ranking.rrf_ranker import compute_rrf_scores
from src.ranking.elite_reranker import elite_rerank
import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def compute_jd_coverage(
    normalized_candidate: Dict[str, Any],
    jd_requirements: Dict[str, List[str]],
    must_weight: int = 4,
    good_weight: int = 1,
) -> float:
    skills = set(normalized_candidate.get("skills_names", []))
    career_text = normalized_candidate.get("career_text", "") or ""
    musts = set(jd_requirements.get("must_have", []))
    goods = set(jd_requirements.get("good_to_have", []))
    matched_must = sum(1 for m in musts if m in skills or m in career_text)
    matched_good = sum(1 for g in goods if g in skills or g in career_text)
    denom = max(must_weight * len(musts) + good_weight * len(goods), 1)
    coverage = (must_weight * matched_must + good_weight * matched_good) / denom
    return float(coverage)


def phase45_pipeline(
    candidates_path: str,
    jd_path: str,
    submission_path: str,
    output_json_path: str | None = None,
    batch_size: int = 10000,
    eligibility_threshold: float = 0.25,
    stage2_k: int = 20000,
    skill_taxonomy_path: str = "configs/skill_taxonomy.yaml",
    weights_path: str = "configs/weights.yaml",
):
    t0 = time.time()
    info("Starting Phase 4.5 pipeline")

    with open(jd_path, "r", encoding="utf-8") as fh:
        jd_text = fh.read()
    jd_parser = JDParser()
    jd_reqs = jd_parser.parse(jd_text)

    taxonomy = load_config(skill_taxonomy_path)
    retrieval_skills = taxonomy.get("retrieval_skills", [])

    if candidates_path.endswith(".gz"):
        from src.ingestion.load_candidates import stream_jsonl_gz as stream
    else:
        stream = stream_jsonl

    all_candidates: List[Dict[str, Any]] = []
    total = 0
    skipped = 0
    t1 = time.time()
    for batch in stream(candidates_path, batch_size=batch_size):
        total += len(batch)
        for record in batch:
            try:
                norm = normalize_candidate(record)
            except Exception as e:
                warning("Failed to normalize candidate {}: {}", record.get("candidate_id"), e)
                skipped += 1
                continue
            eligibility = compute_eligibility(norm, jd_reqs, retrieval_skills, jd_text)
            norm.update(eligibility)
            if eligibility["eligibility_score"] >= eligibility_threshold:
                all_candidates.append(norm)

    t2 = time.time()
    info("Eligibility layer: total={}, skipped={}, eligible={} in {:.2f}s",
         total, skipped, len(all_candidates), t2 - t1)

    # Stage 2a: Cheap features, filter to top-k before expensive features
    t3 = time.time()
    for r in all_candidates:
        depth = compute_retrieval_depth(r)
        maturity = compute_retrieval_maturity(r)
        specialist = compute_retrieval_specialist_probability(r)
        risk = compute_risk_score(r)
        alignment = compute_career_alignment(r)
        behavioral = compute_behavioral_features(r)
        r.update(depth)
        r.update(maturity)
        r.update(specialist)
        r.update(risk)
        r.update(alignment)
        r.update(behavioral)

        cheap_score = (
            0.35 * depth["retrieval_depth"] +
            0.25 * maturity["retrieval_maturity"] +
            0.25 * specialist["retrieval_specialist_probability"] +
            0.15 * alignment["career_alignment_score"]
        )
        r["_cheap_score"] = cheap_score

    all_candidates.sort(key=lambda x: x["_cheap_score"], reverse=True)
    stage2 = all_candidates[:stage2_k]
    info("Stage 2 cheap features computed on {} candidates in {:.2f}s, filtered to {}",
         len(all_candidates), time.time() - t3, len(stage2))

    # Stage 2b: Expensive features
    t4 = time.time()
    rows: List[Dict[str, Any]] = []
    for r in stage2:
        evidence = extract_evidence(r)
        impact = compute_impact_score(r)
        ownership = compute_ownership_score(r)
        quality_v2 = compute_quality_v2(r)
        jd_cov = compute_jd_coverage(r, jd_reqs)

        combined_retrieval = {
            "retrieval_expertise": 0.0,
            "retrieval_depth": r.get("retrieval_depth", 0),
            "retrieval_maturity": r.get("retrieval_maturity", 0),
            "retrieval_specialist_probability": r.get("retrieval_specialist_probability", 0),
            "retrieval_impact": impact["retrieval_impact"],
        }
        intelligence = compute_retrieval_intelligence(combined_retrieval)

        row = {
            "candidate_id": r.get("candidate_id"),
            "profile_title": r.get("profile_title"),
            "years_of_experience": r.get("years_of_experience"),
            "skills_names": r.get("skills_names"),
            "career_text": r.get("career_text"),
            "jd_coverage": jd_cov,
            "evidence_score": evidence.get("evidence_score"),
            "retrieval_expertise": r.get("retrieval_expertise", 0.0),
            "retrieval_intelligence": intelligence["retrieval_intelligence"],
            "retrieval_depth": r.get("retrieval_depth"),
            "retrieval_maturity": r.get("retrieval_maturity"),
            "retrieval_specialist_probability": r.get("retrieval_specialist_probability"),
            "retrieval_impact": impact["retrieval_impact"],
            "career_alignment_score": r.get("career_alignment_score"),
            "ownership_score": ownership["ownership_score"],
            "risk_score": r.get("risk_score"),
            "behavior_super_score": r.get("behavior_super_score"),
            "behavioral_multiplier": r.get("behavioral_multiplier"),
            "availability": r.get("availability"),
            "candidate_quality_v2": quality_v2["candidate_quality_v2"],
            "honeypot_probability": r.get("honeypot_probability"),
            "honeypot_flags": r.get("honeypot_flags"),
        }
        rows.append(row)

    t5 = time.time()
    info("Stage 2b expensive features on {} rows in {:.2f}s", len(rows), t5 - t4)

    # RRF scoring
    rrf_fields = ["retrieval_intelligence", "evidence_score", "career_alignment_score",
                  "ownership_score", "candidate_quality_v2"]
    rows = compute_rrf_scores(rows, rrf_fields, k=60)
    rows.sort(key=lambda x: x["rrf_score"], reverse=True)
    t6 = time.time()
    info("RRF scoring complete in {:.2f}s", t6 - t5)

    # Elite reranker on top 1000
    top_pool = elite_rerank(rows, top_n=1000)
    info("Elite reranker applied to top {} candidates", len(top_pool))

    # Final top-100
    top_100 = top_pool[:100]
    for i, row in enumerate(top_100):
        row["rank"] = i + 1
        row["final_score"] = round(row["elite_score"] * 100.0, 4)
        row["reasoning"] = generate_reasoning(row, i + 1, row["final_score"])

    # Write submission CSV
    os.makedirs(os.path.dirname(submission_path) or ".", exist_ok=True)
    with open(submission_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for row in top_100:
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["final_score"],
                "reasoning": row["reasoning"],
            })

    t7 = time.time()
    info("Submission written to {} ({} rows)", submission_path, len(top_100))
    info("Total Phase 4.5 pipeline time: {:.2f}s", t7 - t0)

    if output_json_path:
        os.makedirs(os.path.dirname(output_json_path) or ".", exist_ok=True)
        serializable = []
        for row in top_100:
            s = dict(row)
            if isinstance(s.get("skills_names"), list):
                s["skills_names"] = [str(x) for x in s["skills_names"]]
            if isinstance(s.get("career_text"), str):
                s["career_text"] = s["career_text"][:500]
            serializable.append(s)
        with open(output_json_path, "w", encoding="utf-8") as fh:
            json.dump(serializable, fh, indent=2, default=str)
        info("Top-100 JSON written to {}", output_json_path)

    return rows


def main():
    parser = argparse.ArgumentParser(description="Phase 4.5 Pipeline")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--jd", required=True)
    parser.add_argument("--submission", default="outputs/phase45_submission.csv")
    parser.add_argument("--output_json", default="outputs/phase45_top100.json")
    parser.add_argument("--batch_size", default=10000, type=int)
    parser.add_argument("--stage2_k", default=20000, type=int)
    parser.add_argument("--eligibility_threshold", default=0.25, type=float)
    parser.add_argument("--skill_taxonomy", default="configs/skill_taxonomy.yaml")
    parser.add_argument("--weights", default="configs/weights.yaml")
    args = parser.parse_args()

    phase45_pipeline(
        candidates_path=args.candidates,
        jd_path=args.jd,
        submission_path=args.submission,
        output_json_path=args.output_json,
        batch_size=args.batch_size,
        stage2_k=args.stage2_k,
        eligibility_threshold=args.eligibility_threshold,
        skill_taxonomy_path=args.skill_taxonomy,
        weights_path=args.weights,
    )


if __name__ == "__main__":
    main()
