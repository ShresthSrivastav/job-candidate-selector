from src.parser.candidate_parser import normalize_candidate
from src.parser.jd_parser import JDParser


def test_normalize_minimal_record():
    result = normalize_candidate({"candidate_id": "C001"})
    assert result["candidate_id"] == "C001"
    assert result["years_of_experience"] == 0.0
    assert result["skills_names"] == []


def test_normalize_with_skills():
    record = {
        "candidate_id": "C001",
        "skills": [{"name": "Python"}, {"name": "FAISS"}],
    }
    result = normalize_candidate(record)
    assert "python" in result["skills_names"]
    assert "faiss" in result["skills_names"]


def test_normalize_empty_record():
    result = normalize_candidate({})
    assert result["candidate_id"] is None


def test_normalize_handles_none_skills():
    record = {"candidate_id": "C001", "skills": None}
    result = normalize_candidate(record)
    assert result["skills_names"] == []


def test_normalize_career_text_contains_summary():
    record = {
        "candidate_id": "C001",
        "profile": {"summary": "Experienced search engineer", "headline": "Staff ML Engineer"},
    }
    result = normalize_candidate(record)
    assert "search engineer" in result["career_text"]
    assert "staff ml engineer" in result["career_text"]


def test_normalize_missing_profile():
    result = normalize_candidate({"candidate_id": "C001"})
    assert result["profile_title"] is None


def test_jd_parse_empty_text():
    parser = JDParser()
    result = parser.parse("")
    assert result["must_have"] == []
    assert result["total_requirements"] == 0


def test_jd_parse_simple():
    parser = JDParser()
    result = parser.parse("Senior Search Engineer with FAISS and Elasticsearch experience.")
    assert "faiss" in result["retrieval_reqs"]


def test_jd_parse_retrieval_terms():
    parser = JDParser()
    result = parser.parse("Must have retrieval ranking and search experience.")
    assert len(result["must_have"]) > 0


def test_normalize_title_bonus():
    record = {"candidate_id": "C001", "profile": {"current_title": "Software Engineer"}}
    result = normalize_candidate(record)
    assert "title_bonus" in result


def test_normalize_handles_none_years():
    record = {"candidate_id": "C001", "profile": {"years_of_experience": None}}
    result = normalize_candidate(record)
    assert result["years_of_experience"] == 0.0
