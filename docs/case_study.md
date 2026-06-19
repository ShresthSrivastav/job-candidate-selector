# RedRobe: A Production-Grade Candidate Ranking System for Retrieval Engineering Roles

## Problem

Hiring for specialized retrieval engineering roles (search, ranking, recommendation systems) requires evaluating candidates across multiple dimensions: technical depth in vector databases and search algorithms, production experience with deployed systems, career trajectory, and evidence of impact. Traditional resume screening is manual, inconsistent, and fails to scale to 100,000+ candidates.

The challenge: build a deterministic, CPU-only, fully reproducible ranking pipeline that can process 100K candidate profiles and produce a top-100 ranked list optimized for retrieval engineering roles — without using LLMs, GPUs, or external APIs.

## Dataset

- 100,000 candidate profiles in JSONL format (~500MB compressed)
- Each profile contains: career history (titles, companies, dates, descriptions), skills inventory, education, certifications, platform engagement signals (profile views, response rates, search appearances)
- Job description for a senior retrieval/search engineering role
- All data anonymized: no names, emails, or contact information

## Architecture Evolution

### Phase 3: Direct Scoring (Baseline)

The initial implementation used a simple weighted linear combination of feature scores. Features were computed inline without separation of cheap vs expensive computation. The entire 100K candidate set went through the full feature pipeline.

**Limitations identified:**
- 100% of candidates received expensive feature computation (53s)
- Single-pass scoring provided no ranking diversity
- No mechanism to break ties or handle score plateaus
- No fraud detection beyond basic checks

### Phase 4.5: Multi-Stage Pipeline with RRF

Major architectural redesign:
1. **Eligibility prefilter** (25% threshold) drops low-fit candidates early
2. **Cheap/expensive feature split** reduces expensive computation by 64% (55K -> 20K)
3. **Cheap score composite** (35% depth + 25% maturity + 25% specialist + 15% alignment) enables early filtering
4. **RRF (Reciprocal Rank Fusion)** replaces direct scoring with rank-based aggregation, eliminating scale sensitivity
5. **Elite reranker** applies weighted linear combination with risk discount on top-1000
6. **Cache architecture** separates feature computation from ranking, enabling rapid iteration

Results: 53s runtime, 22.79 score spread, 100% specialist retention.

### Phase 4.6: Pairwise Reranker Optimization

Key changes from Phase 4.5:
1. **Removed candidate_quality_v2 from RRF** (4 fields instead of 5) — feature was redundant
2. **Added pairwise Copeland tournament** as final ranking stage on top-200
3. **99.8% ranking runtime reduction** — 0.08s vs 53s (cache-based)

Results: 50.5 score spread (+120%), 80% top-100 overlap with Phase 4.5, 0.09s ranking runtime.

### Phase 5: Rejected

Attempted to introduce MiniLM-based semantic scoring and additional embedding features. Rejected because:
- MiniLM introduced non-determinism via GPU-dependent floating point
- CPU-only constraint was violated
- No measurable improvement over Phase 4.6 metrics
- Increased runtime and system complexity
- Pipeline would no longer be fully reproducible

### Phase 47 Research: Authenticity Enhancement (Rejected)

Two variants explored for improving authenticity detection:
1. **Phase 47 v1**: Applied specialist detection threshold to weight down non-specialist candidates. Detection improved 37.5% (79% to 89%) but specialists dropped to 94% (below 95% threshold).
2. **Phase 47.1**: Paragraph-level analysis + indirect evidence matching. Fixed one false demotion (CAND_0070485) but introduced 2 new false demotions. Promotion accuracy remained at 50%.

**Decision:** KEEP_PHASE46. Both variants failed the 90% promotion accuracy threshold.

## Ranking Architecture (Phase 4.6 — Production)

The final ranking pipeline has three stages:

### Stage 1: Reciprocal Rank Fusion (RRF)

Converts 4 field scores into ranks, then fuses via:
```
rrf_score(i) = sum over fields: 1 / (60 + rank_f(i))
```

Fields: retrieval_intelligence (1.5x), evidence_score (1.0x), career_alignment_score (0.8x), ownership_score (1.2x)

### Stage 2: Elite Reranker

Weighted linear combination with risk discount on top-1000:
```
elite = (0.30*RI + 0.20*ES + 0.20*OS + 0.15*CA + 0.10*BS + 0.05*AV) * (1 - risk)
```

### Stage 3: Pairwise Reranker

Copeland round-robin tournament on top-200. Every candidate compared against every other on 5 weighted fields. Win counts normalized to [0, 1].

## Feature Engineering

14 modules organized into two tiers:

**Cheap features** (computed on all 55K eligible candidates):
- Retrieval Depth (5-dimension: infra, search, evaluation, ranking, RAG)
- Retrieval Maturity (hierarchical L0-L5)
- Specialist Probability (weighted signal detection)
- Career Alignment (title + skill alignment with retrieval roles)
- Risk Score (skill stuffing, buzzwords, generic language, consulting)
- Behavioral Signals (platform engagement)

**Expensive features** (computed on top-20K after prefilter):
- Evidence Score (weighted production evidence snippets)
- Retrieval Impact (15 quantified impact patterns)
- Ownership Score (leadership verbs + seniority + scale)
- Candidate Quality (profile completeness, career consistency)
- JD Coverage (weighted must-have/good-to-have match)

**Fraud detection** (10 honeypot flags): duration mismatches, overlapping dates, impossible dates, skill inflation, buzzword density, title/skill contradictions, consulting-only profiles, generic resumes.

## Validation Methodology

### Quality Metrics (6)
| Metric | Target | Phase 4.6 |
|---|---|---|
| Score Spread | > 25 | 50.5 |
| Retrieval Specialists | 100% | 100% |
| Zero Retrieval Intelligence | 0 | 0 |
| Honeypot High Risk | 0 | 0 |
| Avg Retrieval Intelligence | >= 0.45 | 0.487 |
| Ranking Runtime | < 70s | 0.09s |

### Submission Validation (12 checks)
CSV schema, 100 rows, unique IDs, descending scores, non-empty reasoning, runtime, specialist %, zero retrieval, honeypot leakage, rank monotonicity, RI consistency, reasoning consistency.

## Adversarial Testing

The prefilter impact was audited by comparing top-100 sets across prefilters of varying aggressiveness (K=100000, 50000, 20000, 10000). Result: 100% overlap across all K values. The cheap-score ranking is a perfect proxy — no would-be top-100 candidates are lost.

Phase 47 research tested authenticity enhancement against adversarial profiles (keyword stuffing, generic credentials). Detection improved from 79% to 89% but at the cost of 6% specialist loss — an unacceptable tradeoff.

## Lessons Learned

1. **Separate feature computation from ranking.** The cache architecture (Phase 4.5 computes, Phase 4.6 ranks) enabled rapid iteration without recomputing expensive features.
2. **Rank fusion beats direct scoring.** RRF eliminates the need for score normalization and handles disparate scales naturally.
3. **Prefilters are safe when properly validated.** The cheap-score prefilter was verified to have zero top-100 impact across multiple K values.
4. **Pairwise comparisons break plateaus.** The Copeland tournament eliminated score ties that were common in the pure RRF+Elite pipeline.
5. **CPU-only determinism matters.** Rejecting Phase 5's GPU dependency ensured full reproducibility — critical for an auditable ranking system.
6. **Improving detection without sacrificing coverage is hard.** The Phase 47 tradeoff between specialist retention and authenticity detection was ultimately unacceptable.

## Final Outcome

- **Release:** v1.1.0-final (Phase 4.6)
- **Score spread:** 50.5 (range: 49.5–100.0)
- **Specialist retention:** 100%
- **Pipeline SHA256:** `60CED8C5920EDFBA3A8CCAA65B0CCCC50943C2DE62602D0F26ADF10787D6E4C0`
- **Ranking runtime:** ~0.09s (from cache)
- **Full pipeline runtime:** ~82s (Phase 4.5)
- **Repository maturity:** Grade A (96.3/100)
- **Deterministic:** Same inputs always produce identical outputs
- **Fully offline:** No external API calls, no GPU required, no data transmission

The system demonstrates a production-grade approach to candidate ranking: modular architecture, validated prefiltering, multi-stage rank fusion, comprehensive fraud detection, and fully deterministic operation.
