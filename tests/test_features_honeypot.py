from src.features.honeypot_features import detect_honeypot


def test_honeypot_flags_duration_mismatch_overlap():
    ch = [
        {"company": "A", "title": "Eng", "start_date": "2020-01-01", "end_date": "2020-06-01", "duration_months": 2},
        {"company": "B", "title": "Eng", "start_date": "2020-05-01", "end_date": "2021-01-01", "duration_months": 8},
    ]
    cand = {"raw_json": {"career_history": ch, "skills": []}}
    out = detect_honeypot(cand)
    assert "duration_mismatch" in out["honeypot_flags"] or "overlap" in out["honeypot_flags"]
    assert 0.0 <= out["honeypot_probability"] <= 1.0


def test_generic_resume_and_consulting():
    ch = [
        {"company": "X", "title": "Consultant", "start_date": "2022-01-01", "end_date": "2022-04-01", "duration_months": 3, "description": "Did stuff."},
        {"company": "Y", "title": "Consultant", "start_date": "2022-05-01", "end_date": "2022-08-01", "duration_months": 3, "description": "Did stuff."},
        {"company": "Z", "title": "Consultant", "start_date": "2022-09-01", "end_date": "2022-12-01", "duration_months": 3, "description": "Did stuff."},
    ]
    cand = {"raw_json": {"career_history": ch, "skills": [{"name": "Management", "duration_months": 0}]}}
    out = detect_honeypot(cand)
    assert "consulting_only" in out["honeypot_flags"] or "generic_resume" in out["honeypot_flags"]
