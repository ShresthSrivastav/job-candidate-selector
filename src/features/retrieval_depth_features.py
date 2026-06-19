from __future__ import annotations
from typing import Dict, Any, Set


RETRIEVAL_INFRASTRUCTURE = {
    "faiss", "qdrant", "pinecone", "weaviate", "milvus",
    "pgvector", "chromadb", "chroma", "vespa",
}

SEARCH_SYSTEMS = {
    "bm25", "elasticsearch", "opensearch", "lucene", "solr",
    "elastic", "splunk", "algolia", "typesense", "meilisearch",
}

RETRIEVAL_EVALUATION = {
    "ndcg", "mrr", "map", "recall@k", "precision@k",
    "hits@k", "mean average precision", "normalized discounted cumulative gain",
    "recall", "precision",
}

RANKING_SYSTEMS = {
    "ranking", "reranking", "rerank", "recommendation",
    "learning to rank", "ltr", "listwise", "pairwise",
    "pointwise", "ranknet", "lambdarank",
}

RAG_SYSTEMS = {
    "rag", "hybrid search", "query expansion",
    "retrieval augmented generation", "dense retrieval",
    "sparse retrieval", "hybrid retrieval",
}


def _count_matches(text: str, keywords: Set[str]) -> int:
    return sum(1 for k in keywords if k in text)


def compute_retrieval_depth(
    normalized_candidate: Dict[str, Any]
) -> Dict[str, float]:
    skills = " ".join(normalized_candidate.get("skills_names", []) or []).lower()
    career_text = str(normalized_candidate.get("career_text", "") or "").lower()
    combined = skills + " " + career_text

    infra = min(_count_matches(combined, RETRIEVAL_INFRASTRUCTURE) / 3.0, 1.0)
    search = min(_count_matches(combined, SEARCH_SYSTEMS) / 3.0, 1.0)
    evaluation = min(_count_matches(combined, RETRIEVAL_EVALUATION) / 3.0, 1.0)
    ranking = min(_count_matches(combined, RANKING_SYSTEMS) / 3.0, 1.0)
    rag = min(_count_matches(combined, RAG_SYSTEMS) / 2.0, 1.0)

    depth = (
        0.25 * infra +
        0.20 * search +
        0.25 * evaluation +
        0.15 * ranking +
        0.15 * rag
    )
    depth = max(0.0, min(1.0, depth))

    return {
        "retrieval_depth": depth,
        "depth_infra": infra,
        "depth_search": search,
        "depth_evaluation": evaluation,
        "depth_ranking": ranking,
        "depth_rag": rag,
    }
