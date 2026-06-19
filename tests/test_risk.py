from src.features.risk_features import (
    compute_risk_score,
    detect_skill_stuffing,
    detect_buzzword_inflation,
    detect_generic_language,
    detect_consulting_profile,
)


def test_risk_returns_dict_with_all_keys():
    result = compute_risk_score({"skills_names": [], "career_text": ""})
    expected_keys = {"risk_score", "risk_skill_stuffing", "risk_buzzword_inflation", "risk_generic_language", "risk_consulting_profile"}
    assert expected_keys.issubset(result.keys())


def test_risk_zero_inputs_gives_zero_score():
    result = compute_risk_score({"skills_names": [], "career_text": ""})
    assert result["risk_score"] == 0.0


def test_skill_stuffing_above_threshold():
    career = "faiss bm25 qdrant pinecone weaviate milvus elasticsearch opensearch lucene"
    skills = ["solr", "ndcg", "mrr", "rag"]
    score = detect_skill_stuffing(career, skills)
    assert score > 0.0


def test_skill_stuffing_below_threshold():
    career = "faiss bm25"
    skills = []
    score = detect_skill_stuffing(career, skills)
    assert score == 0.0


def test_buzzword_inflation_above_threshold():
    career = "expert with expertise in advanced specialized proficient deep knowledge extensive experience"
    skills = []
    score = detect_buzzword_inflation(career, skills)
    assert score > 0.0


def test_buzzword_inflation_below_threshold():
    career = "expert"
    skills = []
    score = detect_buzzword_inflation(career, skills)
    assert score == 0.0


def test_generic_language_detection():
    text = "team player hardworking dedicated results-oriented detail-oriented excellent communication"
    score = detect_generic_language(text)
    assert score > 0.0


def test_generic_language_empty_text():
    score = detect_generic_language("")
    assert score == 0.0


def test_consulting_profile_detection():
    text = "consultant freelance contractor independent agency"
    score = detect_consulting_profile(text)
    assert score > 0.0


def test_consulting_profile_no_match():
    score = detect_consulting_profile("software engineer at company")
    assert score == 0.0


def test_risk_score_is_max_of_components():
    result = compute_risk_score({
        "skills_names": ["faiss", "bm25", "qdrant", "pinecone", "weaviate", "milvus", "elasticsearch", "opensearch"],
        "career_text": "expert with expertise in advanced specialized",
    })
    stuffing = result["risk_skill_stuffing"]
    buzzword = result["risk_buzzword_inflation"]
    expected = max(stuffing, buzzword)
    assert result["risk_score"] == expected


def test_risk_score_clamped_to_01():
    result = compute_risk_score({
        "skills_names": ["faiss"] * 20,
        "career_text": "expert " * 20 + "team player dedicated " * 10 + "consultant " * 10,
    })
    assert 0.0 <= result["risk_score"] <= 1.0


def test_risk_missing_keys_default_to_zero():
    result = compute_risk_score({})
    assert result["risk_score"] == 0.0
