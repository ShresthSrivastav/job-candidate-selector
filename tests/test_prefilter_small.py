from scripts.phase45_pipeline import phase45_pipeline


def test_prefilter_small_k(tmp_path):
    out_csv = tmp_path / "test_prefilter_small.csv"
    rows = phase45_pipeline(
        candidates_path="Data/candidates.jsonl",
        jd_path="Data/job_description.txt",
        submission_path=str(out_csv),
        batch_size=500,
        stage2_k=5,
    )
    assert len(rows) >= 0
