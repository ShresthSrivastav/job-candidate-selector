# Architecture

## Overview

RedRobe is a candidate ranking pipeline for retrieval engineering roles. It operates in a feed-forward pipeline: raw candidate records → normalization → feature extraction → multi-stage ranking → submission.

## Pipeline Phases

### Phase 4.5 — Baseline Pipeline

```
Raw JSONL → Normalize → Eligibility (25% threshold) → Cheap Features → Top-K (20,000) → Expensive Features → RRF (5 fields) → Elite Reranker → Top-100
```

- Streams 100K candidates from JSONL
- Computes eligibility score; drops candidates below 0.25 threshold
- Computes cheap features (depth, maturity, specialist, risk, alignment, behavioral) on all eligible
- Sorts by cheap score composite, retains top 20,000
- Computes expensive features (evidence, impact, ownership, quality_v2, JD coverage, intelligence) on survivors
- RRF fusion with 5 fields: retrieval_intelligence, evidence_score, career_alignment_score, ownership_score, candidate_quality_v2
- Elite reranker on top-1,000: weighted linear composite with risk discount
- Generates top-100 submission with reasoning strings

### Phase 4.6 — Optimized Pipeline

```
Cache → RRF (4 fields, no quality_v2) → Elite Reranker (top-1,000) → Pairwise Reranker (top-200) → Top-100
```

- Loads pre-computed `.full_cache.pkl` from Phase 4.5 output
- RRF with 4 fields (removed candidate_quality_v2)
- Elite reranker unchanged
- Added pairwise Copeland tournament on top-200
- 99.8% runtime reduction (0.08s vs 53s on expensive features)

### Phase 3 — Original Pipeline (archived)

`archive/research_code/` contains the original Phase 3 pipeline with direct scoring (no RRF, no pairwise).

## Key Design Decisions

| Decision | Rationale |
|---|---|
| CPU-only | Reproducible, deterministic; no GPU/LLM dependency |
| Cache-based architecture | Separates expensive feature computation (Phase 4.5) from ranking optimization (Phase 4.6) |
| Cheap score prefilter | Avoids computing expensive features on low-quality candidates; zero top-100 loss (audited) |
| Pairwise reranker | Breaks score ties and rank plateaus via round-robin comparison |
| No external APIs | Fully self-contained; no LLM, no embedding services |

## Directory Layout

```
src/
  features/        14 feature modules (single-file, pure functions)
  ranking/          3 ranking modules (RRF, Elite, Pairwise)
  parser/           2 parser modules (JD, Candidate)
  ingestion/        1 streaming loader
  utils/            logging utilities
scripts/            3 production scripts (pipeline, optimization, release freeze)
tests/              10+ test files (unit + integration)
docs/               architecture, features, ranking, validation, release, testing, dependencies
outputs/            generated submissions, reports, caches
release_v110/       frozen v1.1.0-final artifacts
archive/            research code, experiments, old reports
```

## Data Flow

```
Data/candidates.jsonl
         │
         ▼
src/ingestion/load_candidates.py  (stream_jsonl, batch_size=10,000)
         │
         ▼
src/parser/candidate_parser.py     (normalize_candidate)
         │
         ▼
src/parser/jd_parser.py            (parse JD into requirements)
         │
         ▼
src/features/                      (14 feature modules)
         │
         ▼
src/ranking/                       (3 ranking stages)
         │
         ▼
outputs/phase46_submission.csv     (final top-100)
```

## Runtime Profile

| Stage | Time | Candidates |
|---|---|---|
| JSONL streaming | ~11s | 100,000 |
| Eligibility + cheap features | ~18s | 55,392 eligible |
| Expensive features | ~53s | 55,392 → 20,000 |
| RRF + Elite + Pairwise | <0.1s | 20,000 → 100 |
| **Total** | ~82s | 20,000 output |

Phase 4.6 ranking (from cache): ~0.09s
