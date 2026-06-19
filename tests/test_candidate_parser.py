from src.parser.candidate_parser import normalize_candidate


def test_normalize_candidate_minimal():
    record = {
        "candidate_id": "CAND_TEST_1",
        "profile": {
            "headline": "ML Engineer | Search",
            "summary": "Worked on retrieval systems.",
            "years_of_experience": 6.5,
            "current_title": "ML Engineer",
        },
        "skills": [{"name": "Faiss"}, {"name": "NLP"}],
        "career_history": [{"description": "Implemented FAISS-based retrieval serving 100k users."}],
    }
    norm = normalize_candidate(record)
    assert norm["candidate_id"] == "CAND_TEST_1"
    assert "faiss" in norm["skills_names"]
    assert norm["years_of_experience"] == 6.5
