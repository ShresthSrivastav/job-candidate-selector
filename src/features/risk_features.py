from __future__ import annotations
from typing import Dict, Any, List, Set

SKILL_STUFFING_PATTERNS: Set[str] = {
    "faiss", "bm25", "qdrant", "pinecone", "weaviate", "milvus",
    "elasticsearch", "opensearch", "lucene", "solr",
    "ndcg", "mrr", "map", "recall@k", "precision@k",
    "rag", "hybrid search", "dense retrieval", "sparse retrieval",
    "vector search", "information retrieval",
}

BUZZWORD_INFLATION_TERMS: Set[str] = {
    "expert", "expertise", "proficient", "advanced", "specialized",
    "deep knowledge", "extensive experience",
}

GENERIC_RESUME_SIGNALS: Set[str] = {
    "team player", "hardworking", "dedicated", "results-oriented",
    "detail-oriented", "excellent communication", "fast learner",
    "self-motivated", "proactive",
}

CONSULTING_SIGNALS: Set[str] = {
    "consultant", "freelance", "contractor", "independent",
    "agency", "outsourced",
}


def detect_skill_stuffing(career_text: str, skills: List[str]) -> float:
    combined = " ".join(skills).lower() + " " + career_text.lower()
    match_count = 0
    for pattern in SKILL_STUFFING_PATTERNS:
        if pattern in combined:
            match_count += 1
    if match_count >= 8:
        return min((match_count - 7) / 10.0, 1.0)
    return 0.0


def detect_buzzword_inflation(career_text: str, skills: List[str]) -> float:
    combined = " ".join(skills).lower() + " " + career_text.lower()
    match_count = 0
    for term in BUZZWORD_INFLATION_TERMS:
        if term in combined:
            match_count += 1
    if match_count >= 4:
        return min((match_count - 3) / 5.0, 1.0)
    return 0.0


def detect_generic_language(career_text: str) -> float:
    text = career_text.lower()
    match_count = 0
    for signal in GENERIC_RESUME_SIGNALS:
        if signal in text:
            match_count += 1
    return min(match_count / 5.0, 1.0)


def detect_consulting_profile(career_text: str) -> float:
    text = career_text.lower()
    match_count = 0
    for signal in CONSULTING_SIGNALS:
        if signal in text:
            match_count += 1
    return min(match_count / 3.0, 1.0)


def compute_risk_score(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    skills = normalized_candidate.get("skills_names", []) or []
    career_text = (normalized_candidate.get("career_text", "") or "")

    stuffing = detect_skill_stuffing(career_text, skills)
    buzzword = detect_buzzword_inflation(career_text, skills)
    generic = detect_generic_language(career_text)
    consulting = detect_consulting_profile(career_text)

    risk_score = max(stuffing, buzzword, generic * 0.5, consulting * 0.3)
    risk_score = max(0.0, min(1.0, risk_score))

    return {
        "risk_score": risk_score,
        "risk_skill_stuffing": stuffing,
        "risk_buzzword_inflation": buzzword,
        "risk_generic_language": generic,
        "risk_consulting_profile": consulting,
    }
