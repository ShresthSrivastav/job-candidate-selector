from __future__ import annotations
from typing import Dict, Any, Set


SPECIALIST_SIGNALS: Set[str] = {
    "faiss", "bm25", "rag", "qdrant", "pinecone",
    "ndcg", "mrr", "map", "ranking", "recommendation",
    "search engineer", "retrieval engineer", "search",
    "retrieval", "elasticsearch", "opensearch", "lucene",
    "reranking", "rerank", "learning to rank", "ltr",
    "vector search", "dense retrieval", "hybrid search",
    "information retrieval", "ir",
}


def compute_retrieval_specialist_probability(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    skills = [s.lower() for s in normalized_candidate.get("skills_names", []) or []]
    career_text = (normalized_candidate.get("career_text", "") or "").lower()
    title = (normalized_candidate.get("profile_title") or "").lower()
    combined = " ".join(skills) + " " + career_text + " " + title

    match_count = 0
    for signal in SPECIALIST_SIGNALS:
        if signal in combined:
            match_count += 1

    weight_map = {
        "faiss": 3, "bm25": 3, "rag": 3, "elasticsearch": 2, "opensearch": 2,
        "ndcg": 4, "mrr": 4, "map": 4, "ranking": 3, "recommendation": 3,
        "search engineer": 5, "retrieval engineer": 5, "search": 2, "retrieval": 3,
        "reranking": 3, "learning to rank": 4,
        "vector search": 2, "dense retrieval": 2, "hybrid search": 2,
        "information retrieval": 4,
    }

    weighted_sum = 0.0
    for signal, weight in weight_map.items():
        if signal in combined:
            weighted_sum += weight

    max_possible = 20.0
    probability = min(weighted_sum / max_possible, 1.0)

    return {
        "retrieval_specialist_probability": probability,
        "retrieval_specialist_signal_count": match_count,
    }
