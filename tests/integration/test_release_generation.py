import sys, os, json, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUTS = os.path.join(ROOT, "outputs")


def test_submission_csv_exists():
    assert os.path.exists(os.path.join(OUTPUTS, "phase46_submission.csv"))


def test_submission_json_exists():
    assert os.path.exists(os.path.join(OUTPUTS, "phase46_top100.json"))


def test_submission_csv_valid():
    with open(os.path.join(OUTPUTS, "phase46_submission.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 100
    assert all(r["candidate_id"] for r in rows)
    assert all(r["rank"] for r in rows)
    assert all(r["score"] for r in rows)
    assert all(r["reasoning"] for r in rows)


def test_submission_json_valid():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 100
    required = {"candidate_id", "rank", "final_score", "reasoning", "retrieval_intelligence", "evidence_score", "ownership_score"}
    for entry in data:
        assert required.issubset(entry.keys())


def test_json_ids_match_csv():
    with open(os.path.join(OUTPUTS, "phase46_submission.csv"), encoding="utf-8") as f:
        csv_ids = {r["candidate_id"] for r in csv.DictReader(f)}
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        json_ids = {r["candidate_id"] for r in json.load(f)}
    assert csv_ids == json_ids


def test_release_manifest_exists():
    assert os.path.exists(os.path.join(ROOT, "release_v110", "MANIFEST.json"))


def test_release_manifest_valid():
    with open(os.path.join(ROOT, "release_v110", "MANIFEST.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    assert "release_version" in manifest
    assert "artifacts" in manifest
    assert len(manifest["artifacts"]) >= 8


def test_release_submission_matches_output():
    with open(os.path.join(OUTPUTS, "phase46_submission.csv"), encoding="utf-8") as f:
        output_content = f.read()
    with open(os.path.join(ROOT, "release_v110", "phase46_submission.csv"), encoding="utf-8") as f:
        release_content = f.read()
    assert output_content == release_content
