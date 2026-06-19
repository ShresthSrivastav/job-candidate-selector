import sys, os, json, csv, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUTS = os.path.join(ROOT, "outputs")
SUBMISSION = os.path.join(OUTPUTS, "phase46_submission.csv")


def test_submission_exists():
    assert os.path.exists(SUBMISSION), f"Submission not found at {SUBMISSION}"


def test_submission_100_rows():
    with open(SUBMISSION, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 100, f"Expected 100 rows, got {len(rows)}"


def test_submission_columns():
    with open(SUBMISSION, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    required = {"candidate_id", "rank", "score", "reasoning"}
    assert required.issubset(rows[0].keys()), f"Missing columns: {required - set(rows[0].keys())}"


def test_scores_descending():
    with open(SUBMISSION, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    scores = [float(r["score"]) for r in rows]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i+1], f"Score not descending at index {i}: {scores[i]} < {scores[i+1]}"


def test_unique_ids():
    with open(SUBMISSION, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = [r["candidate_id"] for r in rows]
    assert len(set(ids)) == 100, f"Duplicate IDs found"


def test_reasoning_not_empty():
    with open(SUBMISSION, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        assert r["reasoning"].strip(), f"Empty reasoning for candidate {r['candidate_id']}"


def test_pipeline_execution():
    script = os.path.join(ROOT, "scripts", "phase46_optimization.py")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
    # Verify output still has 100 rows after execution
    assert os.path.exists(SUBMISSION)
    with open(SUBMISSION) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 100
