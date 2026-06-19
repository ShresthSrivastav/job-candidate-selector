# Validation Methodology

## Quality Metrics

Each ranking run produces 6 validation metrics:

| Metric | Target | Description |
|---|---|---|
| Score Spread | > 25 | Difference between highest and lowest final score |
| Retrieval Specialists % | = 100% | Candidates with retrieval_intelligence >= 0.3 |
| Zero Retrieval Intelligence | = 0 | Candidates with retrieval_intelligence == 0 |
| Honeypot High Risk | = 0 | Candidates with honeypot_probability > 0.8 |
| Avg Retrieval Intelligence | >= 0.45 | Mean retrieval_intelligence across top-100 |
| Runtime | < 70s | Total pipeline execution time |

## Submission Validation (12 Checks)

Before freeze, the submission must pass 12 validations in `phase46_release_freeze.py`:

| # | Check | Criterion |
|---|---|---|
| 1 | CSV_SCHEMA | Columns: candidate_id, rank, score, reasoning |
| 2 | 100_ROWS | Exactly 100 candidates |
| 3 | UNIQUE_IDS | All 100 candidate IDs distinct |
| 4 | SCORES_DESCENDING | Scores monotonically decreasing |
| 5 | REASONING_PRESENT | All reasoning strings non-empty |
| 6 | RUNTIME_LT_70 | Pipeline < 70 seconds |
| 7 | SPECIALISTS_100 | 100% retrieval specialists |
| 8 | ZERO_RETRIEVAL | Zero candidates with 0 retrieval intelligence |
| 9 | HONEYPOT_ZERO | Zero candidates with hp > 0.8 |
| 10 | RANK_MONOTONICITY | Ranks 1..100 with no gaps |
| 11 | RI_CONSISTENCY | RI values align with specialist classification |
| 12 | REASONING_CONSISTENCY | Reasoning strings match score values |

## Prefilter Impact Audit

The stage2_k=20000 prefilter was audited by comparing top-100 sets across K=100000 (disabled), 50000, 20000, and 10000. Result: **100% overlap across all K values**. The prefilter removes zero would-be top-100 candidates.

## Pipeline Verification

SHA256 hash of `outputs/submission.csv` === `release_v110/phase46_submission.csv`:
`60CED8C5920EDFBA3A8CCAA65B0CCCC50943C2DE62602D0F26ADF10787D6E4C0`

## Audit Checks (Phase 4.6 into Phase 4.7 Research)

- Phase 47 authenticity variants: detection improved 89% but promotion accuracy 50%
- Candidates removed from top-100 by Phase 47: validated via overlap analysis
- All research kept in `archive/` for reproducibility
