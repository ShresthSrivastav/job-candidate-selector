from src.features.ownership_features import compute_ownership_score


def test_ownership_returns_dict_with_all_keys():
    result = compute_ownership_score({"career_text": "", "profile_title": ""})
    expected_keys = {"ownership_score", "ownership_verb_count", "ownership_has_seniority", "ownership_scale_score"}
    assert expected_keys.issubset(result.keys())


def test_ownership_zero_inputs_gives_zero_score():
    result = compute_ownership_score({"career_text": "", "profile_title": ""})
    assert result["ownership_score"] == 0.0
    assert result["ownership_verb_count"] == 0
    assert result["ownership_scale_score"] == 0.0


def test_ownership_verbs_contribute_to_score():
    text = "led the team architected the system owned the pipeline drove adoption"
    result = compute_ownership_score({"career_text": text, "profile_title": ""})
    assert result["ownership_verb_count"] >= 4
    assert result["ownership_score"] > 0.0


def test_ownership_seniority_boosts_score():
    result = compute_ownership_score({"career_text": "", "profile_title": "Principal Engineer"})
    assert result["ownership_has_seniority"] is True
    assert result["ownership_score"] > 0.0


def test_ownership_scale_matches_contribute():
    text = "managed millions of users with low-latency real-time systems"
    result = compute_ownership_score({"career_text": text, "profile_title": ""})
    assert result["ownership_scale_score"] >= 2
    assert result["ownership_score"] > 0.0


def test_ownership_score_clamped_to_01():
    text = "led " * 100 + "millions of users low-latency"
    result = compute_ownership_score({"career_text": text, "profile_title": "Principal Staff VP Director"})
    assert 0.0 <= result["ownership_score"] <= 1.0


def test_ownership_missing_keys_default_to_zero():
    result = compute_ownership_score({})
    assert result["ownership_score"] == 0.0
    assert result["ownership_verb_count"] == 0


def test_ownership_full_marks_with_all_signals():
    text = "led architected owned drove spearheaded founded millions of users real-time a/b test"
    result = compute_ownership_score({"career_text": text, "profile_title": "Staff Engineer"})
    assert result["ownership_score"] >= 0.7


def test_ownership_seniority_false_with_plain_title():
    result = compute_ownership_score({"career_text": "", "profile_title": "Software Engineer"})
    assert result["ownership_has_seniority"] is False


def test_ownership_verb_count_with_duplicate_verbs():
    text = "led the team. led another team. led again."
    result = compute_ownership_score({"career_text": text, "profile_title": ""})
    assert result["ownership_verb_count"] == 3
