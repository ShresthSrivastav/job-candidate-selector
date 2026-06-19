from src.features.evidence_features import extract_evidence_from_history


def test_evidence_basic():
    history = [
        {"description": "Implemented a FAISS index and improved throughput by 30%. Served 1M users."},
        {"description": "Worked on pipeline, deployed a retrieval system using Pinecone."},
        {"description": "General maintenance and meetings."},
    ]
    out = extract_evidence_from_history(history)
    assert out["raw_evidence_count"] >= 2
    assert out["evidence_score"] > 0.0
    assert isinstance(out["top_evidence_snippets"], list)


def test_evidence_no_matches():
    history = [{"description": "Worked in HR and managed people."}]
    out = extract_evidence_from_history(history)
    assert out["raw_evidence_count"] == 0
    assert out["evidence_score"] == 0
