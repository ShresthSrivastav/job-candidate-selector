from __future__ import annotations
from typing import Dict, Any, List


def compute_rrf_scores(
    df: List[Dict[str, Any]],
    rank_fields: List[str],
    k: int = 60,
) -> List[Dict[str, Any]]:
    if not df:
        return df

    ranks: Dict[str, List[float]] = {}
    for field in rank_fields:
        sorted_rows = sorted(
            enumerate(df),
            key=lambda x: float(x[1].get(field, 0.0) or 0.0),
            reverse=True,
        )
        field_ranks = [0.0] * len(df)
        for rank_pos, (orig_idx, _) in enumerate(sorted_rows):
            field_ranks[orig_idx] = float(rank_pos + 1)
        ranks[field] = field_ranks

    for i in range(len(df)):
        rrf_score = 0.0
        for field in rank_fields:
            rrf_score += 1.0 / (k + ranks[field][i])
        df[i]["rrf_score"] = rrf_score

    return df
