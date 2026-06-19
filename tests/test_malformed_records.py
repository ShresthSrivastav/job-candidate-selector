"""Tests that the pipeline handles malformed records gracefully."""
from src.parser.candidate_parser import normalize_candidate


def test_null_fields():
    record = {
        "candidate_id": "C001",
        "skills": None,
        "profile": None,
    }
    result = normalize_candidate(record)
    assert result["candidate_id"] == "C001"


def test_partial_profile():
    record = {
        "candidate_id": "C001",
        "profile": {"current_title": "Engineer"},
    }
    result = normalize_candidate(record)
    assert result["profile_title"] == "Engineer"


def test_career_history_none():
    record = {"candidate_id": "C001", "raw_json": {"career_history": None}}
    # normalize_candidate doesn't use raw_json directly for career_text
    result = normalize_candidate(record)
    assert result["candidate_id"] == "C001"


def test_empty_skills_list():
    record = {"candidate_id": "C001", "skills": []}
    result = normalize_candidate(record)
    assert result["skills_names"] == []


def test_skills_without_name():
    record = {"candidate_id": "C001", "skills": [{"level": "expert"}, {"name": "Python"}]}
    result = normalize_candidate(record)
    assert "python" in result["skills_names"]


def test_profile_with_missing_summary():
    record = {"candidate_id": "C001", "profile": {"current_title": "Engineer"}}
    result = normalize_candidate(record)
    assert "career_text" in result


def test_record_with_extra_fields():
    record = {"candidate_id": "C001", "extra_field": "value", "another": 123}
    result = normalize_candidate(record)
    assert result["candidate_id"] == "C001"


def test_unicode_in_fields():
    record = {"candidate_id": "C001", "profile": {"current_title": "Ingénieur Recherche"}}
    result = normalize_candidate(record)
    assert result["profile_title"] is not None


def test_very_long_text():
    record = {"candidate_id": "C001", "profile": {"summary": "x" * 10000, "headline": "Engineer"}}
    result = normalize_candidate(record)
    assert len(result["career_text"]) >= 10000
