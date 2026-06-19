from src.features.career_alignment_features import compute_career_alignment


def test_alignment_returns_dict_with_all_keys():
    result = compute_career_alignment({"profile_title": "", "skills_names": [], "career_text": ""})
    expected_keys = {"career_alignment_score", "career_alignment_signal_count", "career_alignment_is_search_adjacent"}
    assert expected_keys.issubset(result.keys())


def test_alignment_zero_signals_gives_zero_score():
    result = compute_career_alignment({"profile_title": "", "skills_names": [], "career_text": ""})
    assert result["career_alignment_score"] == 0.0
    assert result["career_alignment_signal_count"] == 0


def test_alignment_search_adjacent_title_with_three_signals_gives_one():
    result = compute_career_alignment({
        "profile_title": "Search Engineer",
        "skills_names": ["faiss", "bm25", "rag"],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 1.0
    assert result["career_alignment_is_search_adjacent"] is True


def test_alignment_search_adjacent_with_one_signal_gives_07():
    result = compute_career_alignment({
        "profile_title": "NLP Engineer",
        "skills_names": ["faiss"],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 0.7


def test_alignment_five_signals_no_search_title_gives_08():
    result = compute_career_alignment({
        "profile_title": "Software Engineer",
        "skills_names": ["faiss", "bm25", "rag", "ndcg", "mrr"],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 0.8


def test_alignment_three_signals_no_search_title_gives_05():
    result = compute_career_alignment({
        "profile_title": "Software Engineer",
        "skills_names": ["faiss", "bm25", "rag"],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 0.5


def test_alignment_one_signal_no_search_title_gives_03():
    result = compute_career_alignment({
        "profile_title": "Software Engineer",
        "skills_names": ["faiss"],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 0.3


def test_alignment_generic_title_no_signals_gives_zero():
    result = compute_career_alignment({
        "profile_title": "Frontend Engineer",
        "skills_names": [],
        "career_text": "",
    })
    assert result["career_alignment_score"] == 0.0


def test_alignment_generic_title_less_than_three_signals_capped_at_03():
    result = compute_career_alignment({
        "profile_title": "Backend Engineer",
        "skills_names": ["faiss"],
        "career_text": "",
    })
    assert result["career_alignment_score"] <= 0.3


def test_alignment_signal_count_matches_text():
    text = "I have experience with faiss, bm25, qdrant, and elasticsearch"
    result = compute_career_alignment({
        "profile_title": "ML Engineer",
        "skills_names": ["rag"],
        "career_text": text,
    })
    assert result["career_alignment_signal_count"] >= 4


def test_alignment_missing_keys_default_to_zero():
    result = compute_career_alignment({})
    assert result["career_alignment_score"] == 0.0
    assert result["career_alignment_signal_count"] == 0
