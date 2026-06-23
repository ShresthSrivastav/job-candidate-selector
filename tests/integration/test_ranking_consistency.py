"""Tests that ranking is deterministic and produces expected distributions."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUTS = os.path.join(ROOT, "outputs")
RELEASE = os.path.join(ROOT, "release_v110")


def test_top100_has_exactly_100_entries():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 100


def test_scores_are_descending():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    scores = [float(r["final_score"]) for r in data]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], f"Not descending at {i}: {scores[i]} < {scores[i+1]}"


def test_ranks_consecutive():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    ranks = [r["rank"] for r in data]
    assert ranks == list(range(1, 101))


def test_all_ids_unique():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    ids = [r["candidate_id"] for r in data]
    assert len(set(ids)) == 100


def test_all_specialists():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    ri_values = [float(r.get("retrieval_intelligence", 0) or 0) for r in data]
    specialists = sum(1 for v in ri_values if v >= 0.3)
    assert specialists == 100


def test_zero_honeypot_leakage():
    with open(os.path.join(OUTPUTS, "phase46_top100.json"), encoding="utf-8") as f:
        data = json.load(f)
    hp_values = [float(r.get("honeypot_probability", 0) or 0) for r in data]
    high_risk = sum(1 for v in hp_values if v > 0.8)
    assert high_risk == 0


def test_release_frozen_not_modifiable():
    with open(os.path.join(RELEASE, "FROZEN_STATE.json"), encoding="utf-8") as f:
        state = json.load(f)
    assert state["modification_allowed"] is False
