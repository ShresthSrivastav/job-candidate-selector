# Research History

## Phase 3 (Original Baseline)

The initial implementation used direct weighted scoring without rank fusion or pairwise comparison. Features were computed inline. Retrieved from `archive/research_code/`.

**Status:** Superseded by Phase 4.5/4.6.

## Phase 4.5 (RRF Baseline)

Introduced:
- Multi-stage pipeline with cheap/expensive feature split
- RRF rank fusion with 5 fields
- Elite reranker with risk discount
- Top-K prefilter (20,000 by cheap score)

**Status:** Production baseline. Cache format used by Phase 4.6.

## Phase 4.6 (Current — Production)

Optimizations over Phase 4.5:
- Removed candidate_quality_v2 from RRF (4 fields → 4)
- Added Pairwise Elite Reranker on top-200
- ~99.8% runtime reduction for ranking stage
- Score spread: 22.79 → 50.25 (+120%)
- Top-100 overlap with Phase 4.5: 80%

**Status:** Active production release (v1.1.0-final).

## Phase 5 (Rejected)

Phase 5 attempted to introduce MiniLM-based semantic scoring and additional embedding features. Rejected because:
- MiniLM introduces non-determinism (GPU-dependent)
- CPU-only constraint violated
- No measurable improvement over Phase 4.6 metrics
- Increased runtime and complexity

**Status:** No code in repository. Research notes only.

## Phase 47 Research (A/B Experiments)

Two variants explored for improving authenticity detection:

### Phase 47 — Authenticity v1
- Applied specialist detection threshold to weight down non-specialist candidates
- Detection improved 37.5% (79% → 89%)
- But specialists dropped to 94% (below 95% threshold)
- Edge gains insufficient to offset specialist loss

### Phase 47.1 — Authenticity v2
- Paragraph-level analysis + indirect evidence matching
- Fixed a false demotion (CAND_0070485)
- But introduced 2 new false demotions
- Promotion accuracy still 50%

**Decision:** KEEP_PHASE46. Both Phase 47 variants failed the 90% promotion accuracy threshold.

## Archive Structure

```
archive/
  research/           Phase 47 research branch (4 files)
  research_code/      72 unused code files (Phase 3, experiments)
  research_reports/   84 experimental reports
```

All research is preserved for reproducibility but excluded from the production pipeline.
