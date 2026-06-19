from __future__ import annotations
from typing import Dict, Any, List, Set


RETRIEVAL_SIGNALS: Set[str] = {
    "faiss", "bm25", "rag", "qdrant", "pinecone", "weaviate", "milvus",
    "elasticsearch", "opensearch", "lucene", "solr",
    "ndcg", "mrr", "map", "recall", "precision",
    "ranking", "recommendation", "reranking", "hybrid search",
    "vector search", "dense retrieval", "information retrieval",
}


def compute_career_alignment(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    title = (normalized_candidate.get("profile_title") or "").lower()
    skills = [s.lower() for s in normalized_candidate.get("skills_names", []) or []]
    career_text = (normalized_candidate.get("career_text", "") or "").lower()
    combined = " ".join(skills) + " " + career_text

    retrieval_signal_count = sum(1 for s in RETRIEVAL_SIGNALS if s in combined)

    search_titles = {"search engineer", "retrieval engineer", "recommendation engineer",
                     "ranking engineer", "nlp engineer", "machine learning engineer",
                     "data scientist", "ai engineer", "applied ml engineer"}
    is_search_adjacent = any(t in title for t in search_titles)

    if is_search_adjacent and retrieval_signal_count >= 3:
        alignment = 1.0
    elif is_search_adjacent and retrieval_signal_count >= 1:
        alignment = 0.7
    elif retrieval_signal_count >= 5:
        alignment = 0.8
    elif retrieval_signal_count >= 3:
        alignment = 0.5
    elif retrieval_signal_count >= 1:
        alignment = 0.3
    else:
        alignment = 0.0

    generic_titles = {"frontend engineer", "backend engineer", "full stack developer",
                      "accountant", "hr manager", "graphic designer", "content writer",
                      "sales executive", "marketing manager", "operations manager",
                      "business analyst", "customer support", "project manager",
                      "mechanical engineer", "civil engineer", "java developer",
                      "net developer", "mobile developer", "devops engineer",
                      "cloud engineer", "data engineer"}
    is_generic = any(t in title for t in generic_titles)
    if is_generic and retrieval_signal_count == 0:
        alignment = 0.0
    elif is_generic and retrieval_signal_count < 3:
        alignment = min(alignment, 0.3)

    return {
        "career_alignment_score": alignment,
        "career_alignment_signal_count": retrieval_signal_count,
        "career_alignment_is_search_adjacent": is_search_adjacent,
    }
