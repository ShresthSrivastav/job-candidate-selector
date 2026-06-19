from src.features.eligibility_features import compute_eligibility
from src.features.retrieval_intelligence import compute_retrieval_intelligence
from src.features.honeypot_features import detect_honeypot
from src.features.behavior_features import compute_behavioral_features


def test_eligibility_no_skills():
    result = compute_eligibility({"skills_names": [], "career_text": "", "profile_title": ""}, {"must_have": [], "good_to_have": []}, [""])
    assert 0.0 <= result["eligibility_score"] <= 1.0


def test_eligibility_null_jd():
    result = compute_eligibility({"skills_names": ["faiss"], "career_text": "", "profile_title": "Engineer"}, {"must_have": [], "good_to_have": []}, ["faiss"])
    assert isinstance(result["eligibility_score"], float)


def test_intelligence_all_zero():
    result = compute_retrieval_intelligence({})
    assert result["retrieval_intelligence"] == 0.0


def test_intelligence_single_field():
    result = compute_retrieval_intelligence({"retrieval_expertise": 1.0})
    assert result["retrieval_intelligence"] == 0.30


def test_honeypot_empty_candidate():
    result = detect_honeypot({"raw_json": {"career_history": [], "skills": []}})
    assert result["honeypot_probability"] == 0.0
    assert result["honeypot_flags"] == []


def test_honeypot_missing_raw_json():
    result = detect_honeypot({})
    assert result["honeypot_probability"] >= 0.0


def test_behavioral_missing_signals():
    result = compute_behavioral_features({"raw_json": {}})
    assert result["behavior_super_score"] >= 0.0
    assert result["availability"] >= 0.0


def test_behavioral_empty_signals():
    result = compute_behavioral_features({"raw_json": {"redrob_signals": {}}})
    assert result["behavior_super_score"] >= 0.0
