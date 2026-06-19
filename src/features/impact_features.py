from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

IMPACT_PATTERNS: List[Tuple[re.Pattern, float]] = [
    # Percentage improvements
    (re.compile(r"\b(\d+)\%\s*(?:improvement|gain|increase|reduction|boost|lift|faster)\b", re.IGNORECASE), 3.0),
    (re.compile(r"\b(?:improved|increased|reduced|boosted)\s+(\d+)\%\b", re.IGNORECASE), 3.0),

    # Metric-driven impact (CTR, conversion, revenue)
    (re.compile(r"\b(?:ctr|lift|conversion|revenue)\s*[:\s]*(\d+)\%\b", re.IGNORECASE), 5.0),

    # Throughput multipliers
    (re.compile(r"\b(\d+)x\s*(?:throughput|speedup|faster|improvement)\b", re.IGNORECASE), 5.0),

    # Scale: millions/billions of users/customers/queries/requests
    (re.compile(r"\b(millions?\s*(?:of\s*)?(?:users?|customers?|queries?|requests?))\b", re.IGNORECASE), 5.0),
    (re.compile(r"\b(\d+)\s*(?:million|billion|thousand)\s*(?:users|customers|queries|requests)\b", re.IGNORECASE), 5.0),

    # Shorthand: 50m, 200k, 1b queries/users/requests
    (re.compile(r"\b(\d+)\+?\s*(?:m|k|b)\s*(?:\+)?\s*(?:users?|queries?|requests?|customers?)\b", re.IGNORECASE), 5.0),
    (re.compile(r"\b(?:serving|handling|processing|managing)\s+(\d+)\+?\s*(?:m|k|b)\s*(?:users?|queries?|requests?|customers?)\b", re.IGNORECASE), 5.0),

    # Per-time scale indicators
    (re.compile(r"\b(\d+)\+?\s*(?:m|k|b)?\s*(?:queries|requests|users)\s*(?:per|/)\s*(?:second|month|day|hour)\b", re.IGNORECASE), 5.0),

    # Latency/performance improvements
    (re.compile(r"\b(?:latency|response\s*time|query\s*time)\s*(?:reduction|decreased|cut|down|improved|reduced)\b", re.IGNORECASE), 3.0),

    # Retrieval evaluation metrics with numbers
    (re.compile(r"\b(?:ndcg|mrr|map|recall)\s*[:\s]*(\d+)\b", re.IGNORECASE), 3.0),
    (re.compile(r"\b(?:ndcg|mrr|map|recall)\s*[@_]\s*\d+\b", re.IGNORECASE), 3.0),

    # Experimentation
    (re.compile(r"\b(ab\s*test|a/b\s*test|experiment|a/b\s*experiment)\b", re.IGNORECASE), 1.0),

    # Scale/growth verbs
    (re.compile(r"\b(?:scaled|scale)\s+(?:to|from|for|up)\b", re.IGNORECASE), 3.0),

    # Business impact
    (re.compile(r"\b(?:revenue|cost|efficiency)\s*(?:impact|saving|improvement|reduction)\b", re.IGNORECASE), 3.0),

    # Large number shorthand near production/quality words
    (re.compile(r"\b(?:generated|produced|collected|processed|captured|gathered)\s+(\d+)\+?\s*(?:m|k|b)\b", re.IGNORECASE), 3.0),
    (re.compile(r"\b(\d+)\+?\s*(?:k|m|b)\+?\s*(?:pairs?|samples?|items?|records?|documents?|data)\b", re.IGNORECASE), 3.0),
]


def compute_impact_score(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    career_text = str(normalized_candidate.get("career_text", "") or "").lower()
    total_weight = 0.0
    match_count = 0

    for pattern, weight in IMPACT_PATTERNS:
        found = pattern.findall(career_text)
        if found:
            match_count += len(found)
            total_weight += weight * len(found)

    max_expected = 20.0
    impact = min(total_weight / max_expected, 1.0)

    return {
        "retrieval_impact": impact,
        "impact_raw_weight": total_weight,
        "impact_match_count": match_count,
    }
