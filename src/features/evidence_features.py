from __future__ import annotations
import re
from typing import Dict, List, Any
import math

PRODUCTION_VERBS = {
    "implemented",
    "built",
    "deployed",
    "shipped",
    "launched",
    "designed",
    "engineered",
    "scaled",
    "productionized",
    "served",
}

OUTCOME_TERMS = {
    "users",
    "customers",
    "requests",
    "throughput",
    "latency",
    "ndcg",
    "mrr",
    "map",
    "ctr",
    "conversion",
    "accuracy",
    "%",
    "reduction",
    "increase",
}

TECH_TERMS = {
    "faiss",
    "pinecone",
    "qdrant",
    "bm25",
    "elasticsearch",
    "elasticsearch",
    "opensearch",
    "rag",
    "recommendation",
    "retrieval",
    "ranking",
}


def _split_sentences(text: str) -> List[str]:
    # naive sentence splitter on punctuation
    if not text:
        return []
    parts = re.split(r"(?<=[\.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def extract_evidence_from_history(career_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract evidence snippets and compute score."""
    snippets: List[Dict[str, Any]] = []
    for item in career_history or []:
        desc = item.get("description") if isinstance(item, dict) else None
        if not desc:
            continue
        sents = _split_sentences(desc.lower())
        for s in sents:
            has_prod = any(verb in s for verb in PRODUCTION_VERBS)
            has_out = any(term in s for term in OUTCOME_TERMS)
            has_tech = any(term in s for term in TECH_TERMS)
            if has_prod or has_out or has_tech:
                if has_prod and has_out and has_tech:
                    weight = 5
                elif has_prod and has_tech:
                    weight = 4
                elif has_out and has_tech:
                    weight = 3
                elif has_tech:
                    weight = 1
                else:
                    weight = 0.5
                reasons = []
                if has_prod:
                    reasons.append("production")
                if has_out:
                    reasons.append("outcome")
                if has_tech:
                    reasons.append("technology")
                snippets.append({"snippet": s, "weight": weight, "reasons": reasons})

    raw_count = len(snippets)
    # Calibrated evidence score: bounded using raw evidence count
    # evidence_score = min(log1p(raw_evidence_count)/3, 1)
    evidence_score = float(min(math.log1p(raw_count) / 3.0, 1.0))
    # pick top 5 by weight then by length
    top = sorted(snippets, key=lambda x: (x["weight"], len(x["snippet"])), reverse=True)[:5]
    return {
        "raw_evidence_count": raw_count,
        "evidence_score": evidence_score,
        "top_evidence_snippets": top,
    }


def extract_evidence(normalized_candidate: Dict[str, Any]) -> Dict[str, Any]:
    # normalized_candidate is expected to have 'raw_json' with career_history
    raw = normalized_candidate.get("raw_json", {}) if isinstance(normalized_candidate, dict) else {}
    career_history = raw.get("career_history") if isinstance(raw, dict) else []
    return extract_evidence_from_history(career_history)
