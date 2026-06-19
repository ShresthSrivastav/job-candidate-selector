from src.features.retrieval_depth_features import compute_retrieval_depth
from src.features.retrieval_maturity_features import compute_retrieval_maturity
from src.features.retrieval_specialist_classifier import compute_retrieval_specialist_probability


def test_retrieval_depth_returns_dict():
    result = compute_retrieval_depth({"skills_names": ["faiss"], "career_text": "built search systems"})
    assert isinstance(result, dict)
    assert "retrieval_depth" in result


def test_retrieval_depth_with_skills():
    result = compute_retrieval_depth({"skills_names": ["faiss", "bm25", "elasticsearch"], "career_text": ""})
    assert result["retrieval_depth"] > 0.0


def test_retrieval_depth_no_skills():
    result = compute_retrieval_depth({"skills_names": [], "career_text": ""})
    assert result["retrieval_depth"] == 0.0


def test_retrieval_maturity_returns_dict():
    result = compute_retrieval_maturity({"skills_names": ["faiss"], "career_text": "", "profile_title": ""})
    assert isinstance(result, dict)
    assert "retrieval_maturity" in result


def test_retrieval_maturity_with_signals():
    result = compute_retrieval_maturity({"skills_names": ["faiss", "qdrant", "elasticsearch"], "career_text": "built and deployed retrieval systems", "profile_title": "Search Engineer"})
    assert result["retrieval_maturity"] >= 0.2


def test_retrieval_maturity_empty():
    result = compute_retrieval_maturity({"skills_names": [], "career_text": "", "profile_title": ""})
    assert result["retrieval_maturity"] == 0.0


def test_specialist_probability_returns_dict():
    result = compute_retrieval_specialist_probability({"skills_names": ["faiss"], "career_text": "", "profile_title": ""})
    assert isinstance(result, dict)
    assert "retrieval_specialist_probability" in result


def test_specialist_probability_with_signals():
    result = compute_retrieval_specialist_probability({"skills_names": ["faiss", "bm25", "rag", "ndcg", "mrr"], "career_text": "search engineer", "profile_title": "Search Engineer"})
    assert result["retrieval_specialist_probability"] >= 0.5


def test_specialist_probability_no_signals():
    result = compute_retrieval_specialist_probability({"skills_names": [], "career_text": "", "profile_title": ""})
    assert result["retrieval_specialist_probability"] == 0.0
