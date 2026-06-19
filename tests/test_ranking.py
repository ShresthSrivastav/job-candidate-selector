from src.ranking.rrf_ranker import compute_rrf_scores
from src.ranking.elite_reranker import elite_rerank
from src.ranking.pairwise_elite_v2 import pairwise_rerank_top_n


def make_candidate(cid, ri=0.5, es=0.5, os_=0.5, ca=0.5, bs=0.5, av=0.5, rs=0.0, jd_cov=0.5):
    return {
        "candidate_id": cid,
        "retrieval_intelligence": ri,
        "evidence_score": es,
        "ownership_score": os_,
        "career_alignment_score": ca,
        "behavior_super_score": bs,
        "availability": av,
        "risk_score": rs,
        "jd_coverage": jd_cov,
    }


def test_full_ranking_produces_top_100():
    cands = [make_candidate(f"C{i}", ri=(100 - i) / 100) for i in range(200)]
    rrf = compute_rrf_scores(cands, ["retrieval_intelligence", "evidence_score", "ownership_score", "career_alignment_score"])
    elite = elite_rerank(rrf, top_n=150)
    assert len(elite) == 150
    assert all("elite_score" in c for c in elite)


def test_full_ranking_plus_pairwise():
    cands = [make_candidate(f"C{i}", ri=(200 - i) / 200) for i in range(250)]
    rrf = compute_rrf_scores(cands, ["retrieval_intelligence", "evidence_score"])
    elite = elite_rerank(rrf, top_n=200)
    assert len(elite) == 200
    pw = pairwise_rerank_top_n(elite, top_n=50)
    assert len(pw) == 50
    assert all("pairwise_v2_score" in c for c in pw)


def test_ranking_stability_identical_inputs():
    cands = [make_candidate("C0", ri=0.5), make_candidate("C1", ri=0.5)]
    rrf_a = compute_rrf_scores(cands, ["retrieval_intelligence", "evidence_score"])
    rrf_b = compute_rrf_scores(cands, ["retrieval_intelligence", "evidence_score"])
    scores_a = [r["rrf_score"] for r in rrf_a]
    scores_b = [r["rrf_score"] for r in rrf_b]
    assert scores_a == scores_b


def test_ranking_ordering_by_rrf():
    strong = make_candidate("strong", ri=1.0, es=1.0)
    weak = make_candidate("weak", ri=0.0, es=0.0)
    result = compute_rrf_scores([weak, strong], ["retrieval_intelligence", "evidence_score"])
    result.sort(key=lambda x: x["rrf_score"], reverse=True)
    assert result[0]["candidate_id"] == "strong"


def test_elite_score_reflects_intelligence_weight():
    high_ri = make_candidate("high_ri", ri=1.0, es=0.5, os_=0.5, ca=0.5)
    low_ri = make_candidate("low_ri", ri=0.0, es=0.5, os_=0.5, ca=0.5)
    hi_result = elite_rerank([high_ri], top_n=1)
    lo_result = elite_rerank([low_ri], top_n=1)
    assert hi_result[0]["elite_score"] > lo_result[0]["elite_score"]


def test_pairwise_preserves_top_candidates():
    cands = [make_candidate(f"C{i}", ri=(100 - i) / 100) for i in range(100)]
    rrf = compute_rrf_scores(cands, ["retrieval_intelligence"])
    elite = elite_rerank(rrf, top_n=100)
    pw = pairwise_rerank_top_n(elite, top_n=50)
    top5_pw = {c["candidate_id"] for c in pw[:5]}
    top5_elite = {c["candidate_id"] for c in elite[:5]}
    assert len(top5_pw & top5_elite) >= 3


def test_rankings_deterministic():
    cands = [make_candidate(f"C{i}", ri=(100 - i) / 100, es=(i % 5) / 5) for i in range(50)]
    rrf_a = compute_rrf_scores([dict(c) for c in cands], ["retrieval_intelligence", "evidence_score"])
    rrf_b = compute_rrf_scores([dict(c) for c in cands], ["retrieval_intelligence", "evidence_score"])
    ids_a = [r["candidate_id"] for r in rrf_a]
    ids_b = [r["candidate_id"] for r in rrf_b]
    assert ids_a == ids_b


def test_score_spread_after_full_pipeline():
    cands = [make_candidate(f"C{i}", ri=(200 - i) / 200, es=(100 - i % 100) / 100) for i in range(50)]
    rrf = compute_rrf_scores(cands, ["retrieval_intelligence", "evidence_score", "career_alignment_score"])
    elite = elite_rerank(rrf, top_n=50)
    pw = pairwise_rerank_top_n(elite, top_n=50)
    scores = [c.get("pairwise_v2_score", c.get("elite_score", 0)) for c in pw]
    assert max(scores) >= min(scores)
    assert 0 <= max(scores) <= 1
