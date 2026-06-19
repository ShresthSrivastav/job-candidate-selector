# Ranking System

The ranking pipeline uses three sequential stages: Reciprocal Rank Fusion (RRF), Elite Reranker, and Pairwise Reranker.

## Stage 1: RRF (Reciprocal Rank Fusion)

**Module:** `src/ranking/rrf_ranker.py`

Converts multiple score fields into rank positions, then fuses via the reciprocal formula:

```
rrf_score(i) = Σ 1 / (k + rank_f(i))
```

Where:
- `k = 60` (smoothing constant)
- `rank_f(i)` = position of candidate i when sorted by field f

**Fields (Phase 4.6):**
- retrieval_intelligence (1.5 wt in pairwise)
- evidence_score (1.0)
- career_alignment_score (0.8)
- ownership_score (1.2)

**Removed in Phase 4.6:** candidate_quality_v2 (deemed redundant)

## Stage 2: Elite Reranker

**Module:** `src/ranking/elite_reranker.py`

Weighted linear combination with risk discount. Applied to top-1,000 after RRF.

```
raw = 0.30 × retrieval_intelligence
    + 0.20 × evidence_score
    + 0.20 × ownership_score
    + 0.15 × career_alignment
    + 0.10 × behavior_super_score
    + 0.05 × availability

elite_score = raw × (1.0 - risk_score)
clamped to [0.0, 1.0]
```

## Stage 3: Pairwise Reranker

**Module:** `src/ranking/pairwise_elite_v2.py`

Round-robin Copeland tournament on the top N candidates. Every pair is compared on weighted fields; each field acts as a vote.

```
for each pair (a, b):
    for each (field, weight):
        if a.field > b.field: score_a += weight
        if b.field > a.field: score_b += weight
    if score_a > score_b: a wins
    if score_b > score_a: b wins
    if equal: both tie

pairwise_v2_score = win_count / max_wins
```

**Comparison Fields:**
| Field | Weight |
|---|---|
| retrieval_intelligence | 1.5 |
| ownership_score | 1.2 |
| evidence_score | 1.0 |
| career_alignment_score | 0.8 |
| jd_coverage | 0.5 |

Applied to top-200, returns top-100.

## Ranking Evolution

| Phase | Prefilter | RRF Fields | Elite | Pairwise | Runtime |
|---|---|---|---|---|---|
| 3 | None | Direct scoring | No | No | ~15s |
| 4.5 | 20K by cheap score | 5 fields (incl quality_v2) | Yes (1000) | No | ~53s |
| 4.6 | 20K by cheap score | 4 fields (no quality_v2) | Yes (1000) | Yes (200) | ~0.09s |
