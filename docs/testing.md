# Testing Guide

## Test Types

### Unit Tests
Located in `tests/`, each file tests a single module in isolation.

| File | Module Tested |
|---|---|
| `test_retrieval_intelligence.py` | `retrieval_intelligence.py` |
| `test_features_retrieval.py` | `retrieval_depth_features.py` / `retrieval_maturity_features.py` |
| `test_features_honeypot.py` | `honeypot_features.py` |
| `test_features_quality.py` | `candidate_quality_v2.py` |
| `test_features_evidence.py` | `evidence_features.py` |
| `test_candidate_parser.py` | `candidate_parser.py` |
| `test_jd_parser.py` | `jd_parser.py` |
| `test_ownership.py` | `ownership_features.py` |
| `test_alignment.py` | `career_alignment_features.py` |
| `test_risk.py` | `risk_features.py` |
| `test_reranker.py` | `rrf_ranker.py`, `elite_reranker.py`, `pairwise_elite_v2.py` |
| `test_ranking.py` | Full ranking pipeline (RRF + Elite + Pairwise) |

### Integration Tests
Located in `tests/integration/`.

| File | Tests |
|---|---|
| `test_pipeline.py` | Pipeline execution, submission validation, CSV schema, ranking stability |

### Prefilter Test
| File | Tests |
|---|---|
| `test_prefilter_small.py` | Pipeline with small prefilter K value |

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_ownership.py -v

# Run specific test function
pytest tests/test_ownership.py::test_ownership_returns_dict_with_all_keys -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
```

## Coverage Target

≥ 80% on production modules (`src/`).

Coverage is tracked via `pytest-cov`. Current exclusions:
- `__pycache__` directories
- Test files themselves
- `if __name__ == "__main__":` blocks
- `raise NotImplementedError` / `raise AssertionError`

## Test Conventions

- No external test dependencies (no unittest.mock, no fixtures beyond conftest.py)
- Each test function starts with `test_`
- Simple assert statements preferred over assertion helpers
- Test data constructed inline (no external test data files)
- Tests for pure functions use known input/output pairs

## Conftest

`tests/conftest.py` adds the project root to `sys.path`, enabling imports from `src.`.
