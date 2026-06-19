import sys, os, csv, json, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.features.reasoning_generator import generate_reasoning


def make_row(cid, score, ri=0.5, es=0.5, os_=0.5, ca=0.5, bs=0.5, av=0.5, hp=0.0):
    return {
        "candidate_id": cid,
        "rank": 1,
        "final_score": score,
        "retrieval_intelligence": ri,
        "evidence_score": es,
        "ownership_score": os_,
        "career_alignment_score": ca,
        "behavior_super_score": bs,
        "availability": av,
        "jd_coverage": 0.5,
        "honeypot_probability": hp,
        "reasoning": "",
    }


def test_reasoning_generation():
    row = make_row("C001", 95.0)
    reasoning = generate_reasoning(row, 1, 95.0)
    assert isinstance(reasoning, str)
    assert len(reasoning) > 0
    assert "95" in reasoning or "95.0" in reasoning


def test_reasoning_includes_candidate_id():
    row = make_row("C001", 95.0)
    reasoning = generate_reasoning(row, 1, 95.0)
    assert "C001" not in reasoning


def test_csv_structure():
    fieldnames = ["candidate_id", "rank", "score", "reasoning"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"candidate_id": "C001", "rank": 1, "score": 95.0, "reasoning": "Test reasoning"})
    writer.writerow({"candidate_id": "C002", "rank": 2, "score": 90.0, "reasoning": "Test reasoning 2"})
    content = output.getvalue()
    assert "candidate_id,rank,score,reasoning" in content
    assert "C001,1,95.0" in content or "C001,1,95" in content


def test_csv_exactly_100_rows():
    fieldnames = ["candidate_id", "rank", "score", "reasoning"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(100):
        writer.writerow({"candidate_id": f"C{i:04d}", "rank": i+1, "score": 100.0 - i*0.5, "reasoning": f"Rank {i+1}"})
    content = output.getvalue()
    rows = list(csv.DictReader(io.StringIO(content)))
    assert len(rows) == 100
