from src.features.retrieval_intelligence import compute_retrieval_intelligence


def test_all_weights_sum_to_score_in_01():
    features = {
        "retrieval_expertise": 1.0,
        "retrieval_depth": 1.0,
        "retrieval_maturity": 1.0,
        "retrieval_specialist_probability": 1.0,
        "retrieval_impact": 1.0,
    }
    out = compute_retrieval_intelligence(features)
    score = out["retrieval_intelligence"]
    assert 0.0 <= score <= 1.0


def test_high_expertise_gives_high_intelligence():
    features = {
        "retrieval_expertise": 1.0,
        "retrieval_depth": 0.0,
        "retrieval_maturity": 0.0,
        "retrieval_specialist_probability": 0.0,
        "retrieval_impact": 0.0,
    }
    out = compute_retrieval_intelligence(features)
    assert out["retrieval_intelligence"] == 0.30


def test_zero_inputs_give_zero_output():
    features = {
        "retrieval_expertise": 0.0,
        "retrieval_depth": 0.0,
        "retrieval_maturity": 0.0,
        "retrieval_specialist_probability": 0.0,
        "retrieval_impact": 0.0,
    }
    out = compute_retrieval_intelligence(features)
    assert out["retrieval_intelligence"] == 0.0


def test_depth_contribution():
    out = compute_retrieval_intelligence({"retrieval_depth": 1.0})
    assert out["retrieval_intelligence"] == 0.20


def test_maturity_contribution():
    out = compute_retrieval_intelligence({"retrieval_maturity": 1.0})
    assert out["retrieval_intelligence"] == 0.20


def test_specialist_contribution():
    out = compute_retrieval_intelligence({"retrieval_specialist_probability": 1.0})
    assert out["retrieval_intelligence"] == 0.15


def test_impact_contribution():
    out = compute_retrieval_intelligence({"retrieval_impact": 1.0})
    assert out["retrieval_intelligence"] == 0.15


def test_expertise_has_highest_weight():
    expertise_only = compute_retrieval_intelligence({"retrieval_expertise": 1.0})["retrieval_intelligence"]
    depth_only = compute_retrieval_intelligence({"retrieval_depth": 1.0})["retrieval_intelligence"]
    assert expertise_only > depth_only


def test_max_clamped_to_1_0():
    features = {
        "retrieval_expertise": 5.0,
        "retrieval_depth": 5.0,
        "retrieval_maturity": 5.0,
        "retrieval_specialist_probability": 5.0,
        "retrieval_impact": 5.0,
    }
    out = compute_retrieval_intelligence(features)
    assert out["retrieval_intelligence"] == 1.0


def test_missing_keys_default_to_zero():
    out = compute_retrieval_intelligence({})
    assert out["retrieval_intelligence"] == 0.0
