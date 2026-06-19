from src.features.candidate_quality_v2 import compute_quality_v2


def test_quality_v2_returns_dict():
    result = compute_quality_v2({
        "raw_json": {"profile": {}, "career_history": [], "redrob_signals": {}},
        "years_of_experience": 5,
        "skills_names": [],
        "career_text": "",
    })
    assert isinstance(result, dict)
    assert "candidate_quality_v2" in result
    assert "profile_completeness" in result


def test_quality_v2_score_in_range():
    result = compute_quality_v2({
        "raw_json": {"profile": {}, "career_history": [], "redrob_signals": {}},
        "years_of_experience": 5,
        "skills_names": [],
        "career_text": "",
    })
    assert 0.0 <= result["candidate_quality_v2"] <= 1.0


def test_quality_v2_missing_keys():
    result = compute_quality_v2({})
    assert "candidate_quality_v2" in result
