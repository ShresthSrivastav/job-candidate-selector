from src.features.evidence_features import extract_evidence_from_history, extract_evidence


def test_extract_evidence_empty_history():
    result = extract_evidence_from_history([])
    assert result["evidence_score"] == 0.0
    assert result["raw_evidence_count"] == 0


def test_extract_evidence_no_career_history():
    result = extract_evidence({"raw_json": {}})
    assert result["evidence_score"] == 0.0


def test_evidence_counts_production_verbs():
    ch = [{"description": "implemented a search system. built the ranking pipeline. deployed to production."}]
    result = extract_evidence_from_history(ch)
    assert result["raw_evidence_count"] > 0


def test_evidence_counts_outcome_terms():
    ch = [{"description": "improved ndcg by 15% and reduced latency for millions of users."}]
    result = extract_evidence_from_history(ch)
    assert result["raw_evidence_count"] > 0


def test_evidence_top_snippets_limited():
    ch = [{"description": f"implemented retrieval system {i}."} for i in range(20)]
    result = extract_evidence_from_history(ch)
    assert len(result["top_evidence_snippets"]) <= 5


def test_evidence_score_bounded():
    ch = [{"description": "implemented. built. deployed. launched. optimized. scaled."}]
    result = extract_evidence_from_history(ch)
    assert 0.0 <= result["evidence_score"] <= 1.0


def test_evidence_no_matches():
    ch = [{"description": "attended meetings. wrote emails. managed calendar."}]
    result = extract_evidence_from_history(ch)
    assert result["evidence_score"] == 0.0


def test_evidence_extract_wrapper():
    cand = {"raw_json": {"career_history": [{"description": "built faiss index for retrieval"}]}}
    result = extract_evidence(cand)
    assert "evidence_score" in result
    assert "top_evidence_snippets" in result


def test_evidence_snippets_have_required_keys():
    ch = [{"description": "implemented search ranking with ndcg optimization for 10M users."}]
    result = extract_evidence_from_history(ch)
    if result["top_evidence_snippets"]:
        snippet = result["top_evidence_snippets"][0]
        assert "snippet" in snippet
        assert "weight" in snippet
        assert "reasons" in snippet


def test_evidence_missing_description():
    ch = [{"description": None}, {}]
    result = extract_evidence_from_history(ch)
    assert result["evidence_score"] == 0.0
