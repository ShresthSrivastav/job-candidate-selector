from __future__ import annotations
from typing import Dict, Any, List


def compute_elite_score(row: Dict[str, Any]) -> float:
    retrieval_intelligence = float(row.get("retrieval_intelligence", 0.0) or 0.0)
    evidence_score = float(row.get("evidence_score", 0.0) or 0.0)
    ownership_score = float(row.get("ownership_score", 0.0) or 0.0)
    career_alignment = float(row.get("career_alignment_score", 0.0) or 0.0)
    behavior_super_score = float(row.get("behavior_super_score", 0.0) or 0.0)
    availability = float(row.get("availability", 0.0) or 0.0)
    risk_score = float(row.get("risk_score", 0.0) or 0.0)

    raw = (
        0.30 * retrieval_intelligence +
        0.20 * evidence_score +
        0.20 * ownership_score +
        0.15 * career_alignment +
        0.10 * behavior_super_score +
        0.05 * availability
    )

    elite = raw * (1.0 - risk_score)
    return max(0.0, min(1.0, elite))


def elite_rerank(top_candidates: List[Dict[str, Any]], top_n: int = 1000) -> List[Dict[str, Any]]:
    if not top_candidates:
        return []

    pool = top_candidates[:top_n]
    for row in pool:
        row["elite_score"] = compute_elite_score(row)

    pool.sort(key=lambda x: x["elite_score"], reverse=True)
    return pool
