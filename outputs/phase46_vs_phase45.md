# Phase 4.6 vs Phase 4.5 Comparison

**Timestamp:** 2026-06-23 08:54:28

## Pipeline Comparison

| Aspect | Phase 4.5 | Phase 4.6 |
|---|---|---|
| Eligibility | PASS | PASS |
| Cheap Features | PASS | PASS |
| Expensive Features | PASS | PASS |
| RRF Fields | 5 fields (incl quality_v2) | 4 fields (no quality_v2) |
| Elite Reranker | PASS | PASS |
| Pairwise Reranker | FAIL | PASS (top 200) |
| Runtime | 52.85s | 0.07s |

## Metric Comparison

| Metric | Phase 4.5 | Phase 4.6 | Delta | Better? |
|---|---|---|---|---|
| Score Spread | 22.79 | 50.5 | +27.71 | PASS |
| Specialists % | 100.0 | 100.0 | +0 | PASS |
| Zero Ret | 0 | 0 | 0 | PASS |
| HP Risk | 0 | 0 | 0 | PASS |
| Runtime | 52.85s | 0.07s | -52.78s | PASS |
| Avg Ret Intel | 0.4687 | 0.4867 | +0.018 | PASS |

## Top-100 Overlap

**80%** of candidates overlap between Phase 4.5 and Phase 4.6 top-100.

## Decision

**UPGRADE_TO_PHASE46**
