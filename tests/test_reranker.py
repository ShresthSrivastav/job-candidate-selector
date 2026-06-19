from src.ranking.rrf_ranker import compute_rrf_scores
from src.ranking.elite_reranker import compute_elite_score, elite_rerank
from src.ranking.pairwise_elite_v2 import pairwise_rerank_top_n, _pairwise_win


def make_candidate(cid, ri=0.5, es=0.5, os_=0.5, ca=0.5, bs=0.5, av=0.5, rs=0.0):
    return {
        "candidate_id": cid,
        "retrieval_intelligence": ri,
        "evidence_score": es,
        "ownership_score": os_,
        "career_alignment_score": ca,
        "behavior_super_score": bs,
        "availability": av,
        "risk_score": rs,
    }


# --- RRF ---

def test_rrf_returns_list():
    result = compute_rrf_scores([make_candidate("A"), make_candidate("B")], ["retrieval_intelligence", "evidence_score"])
    assert isinstance(result, list)
    assert len(result) == 2


def test_rrf_adds_rrf_score_key():
    cand = make_candidate("A")
    result = compute_rrf_scores([cand], ["retrieval_intelligence"])
    assert "rrf_score" in result[0]


def test_rrf_better_candidate_gets_higher_score():
    weak = make_candidate("weak", ri=0.1, es=0.1)
    strong = make_candidate("strong", ri=0.9, es=0.9)
    result = compute_rrf_scores([weak, strong], ["retrieval_intelligence", "evidence_score"])
    scores = {r["candidate_id"]: r["rrf_score"] for r in result}
    assert scores["strong"] > scores["weak"]


def test_rrf_empty_input():
    result = compute_rrf_scores([], ["retrieval_intelligence"])
    assert result == []


def test_rrf_single_candidate():
    result = compute_rrf_scores([make_candidate("A")], ["retrieval_intelligence"])
    assert result[0]["rrf_score"] > 0


# --- Elite Reranker ---

def test_elite_score_returns_float():
    cand = make_candidate("A")
    score = compute_elite_score(cand)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_elite_score_high_intelligence():
    cand = make_candidate("A", ri=1.0, es=1.0, os_=1.0, ca=1.0, bs=1.0, av=1.0, rs=0.0)
    score = compute_elite_score(cand)
    assert abs(score - 1.0) < 0.01


def test_elite_score_risk_reduces_elite():
    low_risk = make_candidate("A", rs=0.0)
    high_risk = make_candidate("B", rs=0.5)
    assert compute_elite_score(low_risk) >= compute_elite_score(high_risk)


def test_elite_score_zero_inputs():
    cand = make_candidate("A", ri=0, es=0, os_=0, ca=0, bs=0, av=0, rs=0)
    assert compute_elite_score(cand) == 0.0


def test_elite_rerank_sorts_by_elite_score():
    weak = make_candidate("weak", ri=0.1)
    strong = make_candidate("strong", ri=0.9)
    result = elite_rerank([weak, strong], top_n=2)
    assert result[0]["candidate_id"] == "strong"
    assert result[1]["candidate_id"] == "weak"


def test_elite_rerank_empty_input():
    assert elite_rerank([], top_n=10) == []


def test_elite_rerank_respects_top_n():
    cands = [make_candidate(f"C{i}", ri=i / 10) for i in range(10)]
    result = elite_rerank(cands, top_n=3)
    assert len(result) == 3


# --- Pairwise ---

def test_pairwise_win_returns_tuple():
    a = make_candidate("A", ri=0.9)
    b = make_candidate("B", ri=0.1)
    fields = [("retrieval_intelligence", 1.0)]
    result = _pairwise_win(a, b, fields)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_pairwise_win_a_beats_b():
    a = make_candidate("A", ri=0.9)
    b = make_candidate("B", ri=0.1)
    fields = [("retrieval_intelligence", 1.0)]
    winner, score = _pairwise_win(a, b, fields)
    assert winner == "A"
    assert score == 1.0


def test_pairwise_win_tie():
    a = make_candidate("A", ri=0.5)
    b = make_candidate("B", ri=0.5)
    fields = [("retrieval_intelligence", 1.0)]
    winner, score = _pairwise_win(a, b, fields)
    assert score == 0.5


def test_pairwise_rerank_sorts_top_n():
    cands = [make_candidate(f"C{i}", ri=(10 - i) / 10) for i in range(10)]
    result = pairwise_rerank_top_n(cands, top_n=5)
    assert len(result) == 5
    scores = [r["pairwise_v2_score"] for r in result]
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


def test_pairwise_rerank_adds_pairwise_v2_score():
    cands = [make_candidate(f"C{i}", ri=(10 - i) / 10) for i in range(10)]
    result = pairwise_rerank_top_n(cands, top_n=5)
    assert "pairwise_v2_score" in result[0]


def test_pairwise_rerank_below_top_n_returns_sorted_by_rrf():
    cands = [make_candidate(f"C{i}", ri=(10 - i) / 10) for i in range(3)]
    result = pairwise_rerank_top_n(cands, top_n=5)
    assert len(result) == 3


def test_pairwise_rerank_keep_rest_appends_remaining():
    cands = [make_candidate(f"C{i}", ri=(10 - i) / 10) for i in range(10)]
    result = pairwise_rerank_top_n(cands, top_n=5, keep_rest=True)
    assert len(result) == 10
