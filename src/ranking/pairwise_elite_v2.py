from __future__ import annotations
from typing import Dict, Any, List, Tuple

COMPARISON_FIELDS: List[Tuple[str, float]] = [
    ("retrieval_intelligence", 1.5),
    ("ownership_score", 1.0),
    ("retrieval_impact", 1.0),
    ("retrieval_graph_score", 1.0),
    ("career_progression_score", 0.8),
    ("retrieval_maturity", 0.6),
]


def _pairwise_win(
    a: Dict[str, Any], b: Dict[str, Any], fields: List[Tuple[str, float]]
) -> Tuple[str, float]:
    score_a = 0.0
    score_b = 0.0
    for field, weight in fields:
        va = float(a.get(field, 0) or 0)
        vb = float(b.get(field, 0) or 0)
        if va > vb:
            score_a += weight
        elif vb > va:
            score_b += weight
    if score_a > score_b:
        return (a["candidate_id"], 1.0)
    elif score_b > score_a:
        return (b["candidate_id"], 0.0)
    return (a["candidate_id"], 0.5)


def pairwise_rerank_top_n(
    candidates: List[Dict[str, Any]],
    top_n: int = 200,
    keep_rest: bool = False,
) -> List[Dict[str, Any]]:
    if len(candidates) <= top_n:
        if not keep_rest:
            candidates.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        return candidates

    top_pool = candidates[:top_n]
    rest = candidates[top_n:] if keep_rest else []

    n = len(top_pool)
    win_counts: Dict[str, float] = {c["candidate_id"]: 0.0 for c in top_pool}
    for i in range(n):
        for j in range(i + 1, n):
            winner, score = _pairwise_win(top_pool[i], top_pool[j], COMPARISON_FIELDS)
            if score == 0.5:
                win_counts[top_pool[i]["candidate_id"]] += 0.5
                win_counts[top_pool[j]["candidate_id"]] += 0.5
            else:
                win_counts[winner] += 1.0

    max_wins = max(win_counts.values()) if win_counts else 1
    for c in top_pool:
        c["pairwise_v2_score"] = round(win_counts[c["candidate_id"]] / max(max_wins, 1), 4)

    top_pool.sort(key=lambda x: x["pairwise_v2_score"], reverse=True)

    if keep_rest:
        return top_pool + rest
    return top_pool
