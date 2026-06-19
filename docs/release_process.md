# Release Process

## Pipeline

The release process has 3 stages:

### Stage 1: Phase 4.5 — Feature Computation

```
python scripts/phase45_pipeline.py \
  --candidates Data/candidates.jsonl \
  --jd Data/job_description.txt \
  --submission outputs/phase45_submission.csv \
  --stage2_k 20000
```

- Streams 100K candidates from JSONL
- Computes eligibility, cheap features, prefilter, expensive features
- Outputs: submission CSV, top-100 JSON
- Caches full feature matrix to `.full_cache.pkl`

### Stage 2: Phase 4.6 — Ranking Optimization

```
python scripts/phase46_optimization.py
```

- Loads cache from Stage 1
- RRF (4 fields), Elite (top-1000), Pairwise (top-200)
- Generates: `phase46_submission.csv`, `phase46_top100.json`, reports
- Validates against success criteria

### Stage 3: Phase 4.6 Release Freeze

```
python scripts/phase46_release_freeze.py
```

- 12 validation checks (see validation.md)
- Copies artifacts to `release_v110/`
- Generates MANIFEST.json with SHA256 hashes
- Generates SUBMISSION_CERTIFICATE.md
- Sets FROZEN_STATE.json: `modification_allowed: false`

## Release Artifacts

All artifacts are frozen in `release_v110/`:

| Artifact | Description |
|---|---|
| VERSION | Version string: v1.1.0-final |
| FROZEN_STATE.json | Freeze metadata |
| MANIFEST.json | Artifact manifest with SHA256 |
| SUBMISSION_CERTIFICATE.md | Certification report |
| phase46_submission.csv | Final ranked candidate list |
| phase46_top100.json | Full candidate data |
| phase46_report.md | Optimization report |
| phase46_vs_phase45.md | Comparison report |
| phase46_submission_audit.md | Validation audit |
| phase46_submission_audit.json | Validation audit JSON |

## Verification

After release freeze, verify:

```bash
# Pipeline produces identical output
sha256sum outputs/phase46_submission.csv
sha256sum release_v110/phase46_submission.csv
# Should match: 60CED8C5920EDFBA3A8CCAA65B0CCCC50943C2DE62602D0F26ADF10787D6E4C0
```

## Version History

| Version | Date | Phase | Changes |
|---|---|---|---|
| v1.0.0 | — | Phase 3 | Original pipeline |
| v1.1.0-final | — | Phase 4.6 | RRF+Elite+Pairwise, 4 fields, optimized |
