from __future__ import annotations
from typing import Dict, Any


def compute_retrieval_maturity(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    skills = [s.lower() for s in normalized_candidate.get("skills_names", []) or []]
    career_text = (normalized_candidate.get("career_text", "") or "").lower()
    title = (normalized_candidate.get("profile_title") or "").lower()
    combined = " ".join(skills) + " " + career_text + " " + title

    level = 0

    # Level 1: Vector DB user
    vector_db_terms = {"faiss", "pinecone", "qdrant", "weaviate", "milvus", "pgvector", "chroma", "vector database"}
    if any(t in combined for t in vector_db_terms):
        level = max(level, 1)

    # Level 2: Built retrieval systems
    build_terms = {"bm25", "elasticsearch", "opensearch", "lucene", "solr", "built", "implemented", "developed"}
    if any(t in combined for t in build_terms):
        level = max(level, 2)

    # Level 3: Evaluated retrieval systems
    eval_terms = {"ndcg", "mrr", "map", "recall@k", "precision@k", "evaluation", "evaluated", "ab test", "a/b test"}
    if any(t in combined for t in eval_terms):
        level = max(level, 3)

    # Level 4: Production retrieval
    prod_terms = {"production", "deployed", "latency", "throughput", "scaled", "serving"}
    if any(t in combined for t in prod_terms) and level >= 2:
        level = max(level, 4)

    # Level 5: Search/recommendation ownership
    own_terms = {"search engineer", "retrieval engineer", "recommendation engineer",
                 "lead", "staff", "principal", "architected", "owned"}
    if any(t in combined for t in own_terms):
        level = max(level, 5)

    maturity_score = level / 5.0

    return {
        "retrieval_maturity": maturity_score,
        "retrieval_maturity_level": level,
    }
