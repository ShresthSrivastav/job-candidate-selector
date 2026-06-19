# Feature Engineering

## Feature Categories

14 feature modules extract signals from normalized candidate records.

### Eligibility Features

**Module:** `src/features/eligibility_features.py`

Determines minimum candidate fit before full computation.

| Component | Weight | Description |
|---|---|---|
| JD must-have coverage | 40% | Weighted match (must=4x, good=1x) of JD requirements |
| Years-of-experience fit | 30% | Peaked at 7 years (Gaussian-ish decay) |
| Retrieval skill presence | 20% | Fraction of 5 key retrieval skills present |
| Title match | 10% | Does title contain search/retrieval keywords |

Threshold: eligibility_score >= 0.25.

### Cheap Features (Stage 2a)

Computed on ALL eligible candidates before prefilter.

| Feature | Module | Weight in Cheap Score | Description |
|---|---|---|---|
| Retrieval Depth | `retrieval_depth_features.py` | 35% | 5-dimension depth: infra, search, evaluation, ranking, RAG |
| Retrieval Maturity | `retrieval_maturity_features.py` | 25% | Hierarchical level 0-5 (L1=vector DB, L5=search owner) |
| Specialist Probability | `retrieval_specialist_classifier.py` | 25% | Weighted keyword match against specialist signals |
| Career Alignment | `career_alignment_features.py` | 15% | Title+skills+text alignment with retrieval/search roles |
| Risk Score | `risk_features.py` | — | Penalty signal (max of stuffing, buzzwords, generic, consulting) |
| Behavioral | `behavior_features.py` | — | Platform engagement (response rate, views, recency) |

### Expensive Features (Stage 2b)

Computed only on top-K after cheap score prefilter.

| Feature | Module | Used In | Description |
|---|---|---|---|
| Evidence Score | `evidence_features.py` | RRF, Elite | Weighted count of production+outcome+tech evidence snippets |
| Impact Score | `impact_features.py` | Intelligence | 15 regex patterns for quantified impact (% improvements, x throughput, scale) |
| Ownership Score | `ownership_features.py` | RRF, Elite, Pairwise | Leadership verbs + seniority title + scale indicators |
| Candidate Quality v2 | `candidate_quality_v2.py` | Phase 4.5 RRF | Profile completeness (40%) + career consistency (35%) + engagement (25%) |
| JD Coverage | `evidence_features.py` (during pipeline) | Pairwise | Weighted must-have/good-to-have JD skill match |
| Retrieval Intelligence | `retrieval_intelligence.py` | RRF, Elite, Pairwise | Composite: 30% expertise + 20% depth + 20% maturity + 15% specialist + 15% impact |

### Fraud Detection

| Module | Purpose |
|---|---|
| `honeypot_features.py` | 10 flag types: duration mismatch, overlaps, impossible dates, skill inflation, buzzword density, contradiction, consulting-only, generic resume |

### Reasoning

| Module | Purpose |
|---|---|
| `reasoning_generator.py` | Builds human-readable explanation string from feature values |

## Feature Summary Table

| Feature | Type | Range | Used In |
|---|---|---|---|
| eligibility_score | Threshold | [0, 1] | Prefilter (≥0.25) |
| retrieval_depth | Cheap | [0, 1] | Cheap score (35%), Intelligence |
| retrieval_maturity | Cheap | [0, 1] | Cheap score (25%), Intelligence, Pairwise |
| retrieval_specialist_probability | Cheap | [0, 1] | Cheap score (25%), Intelligence |
| career_alignment_score | Cheap | [0, 1] | Cheap score (15%), RRF, Elite, Pairwise |
| risk_score | Cheap | [0, 1] | Penalty in Elite (1-risk) |
| behavior_super_score | Cheap | [0, 1] | Elite (10%) |
| behavioral_multiplier | Cheap | [0.5, 1.5] | Multiplier |
| availability | Cheap | [0, 1] | Elite (5%) |
| evidence_score | Expensive | [0, 1] | RRF, Elite, Pairwise |
| retrieval_impact | Expensive | [0, 1] | Intelligence, Pairwise |
| ownership_score | Expensive | [0, 1] | RRF, Elite, Pairwise |
| candidate_quality_v2 | Expensive | [0, 1] | Phase 4.5 RRF only |
| jd_coverage | Expensive | [0, 1] | Pairwise |
| retrieval_intelligence | Composite | [0, 1] | RRF, Elite, Pairwise |
| honeypot_probability | Audit | [0, 0.99] | Validation |

## Weights

Skill weights are defined in `configs/weights.yaml`:
- faiss=4, bm25=4, hybrid=5, elasticsearch=4, qdrant=3, pinecone=3, rag=5, ndcg=5, mrr=5, map=5, recommendation=4
- skill_trust_multiplier=1.0, evidence_multiplier=1.8
