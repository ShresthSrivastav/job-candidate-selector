# Dependencies

## Production Dependencies

| Package | Version | Purpose | Used In |
|---|---|---|---|
| streamlit | >=1.30.0 | Web UI framework for dashboard | Dashboard only. NOT used by pipeline |
| pandas | >=2.0.0 | Data manipulation and CSV output | Pipeline output processing |
| plotly | >=5.15.0 | Interactive charts for dashboard | Dashboard only. NOT used by pipeline |
| numpy | >=1.24.0 | Numerical operations | Feature computations and score aggregation |
| pyyaml | >=6.0 | YAML configuration parsing | `configs/weights.yaml`, `configs/skill_taxonomy.yaml` |

**Note:** streamlit, plotly are optional UI dependencies. The production pipeline can run without them.

## Development Dependencies

| Package | Version | Purpose | Used In |
|---|---|---|---|
| pytest | >=7.0 | Test runner | `tests/`, `tests/integration/` |
| pytest-cov | >=4.0 | Coverage reporting | Coverage measurement |
| mypy | >=1.0 | Static type checking | Type correctness |
| coverage | >=7.0 | Code coverage measurement | Coverage reports |
| black | >=24.0 | Code formatter | Code style enforcement |
| isort | >=5.0 | Import sorter | Import ordering |
| flake8 | >=7.0 | Linter | Code quality checks |

## Optional Dependencies

| Package | Purpose |
|---|---|
| pre-commit | Git hook management for automated formatting |

## Dependency Graph

```
requirements.txt
├── streamlit (dashboard UI)
├── pandas (CSV/manipulation)
├── plotly (dashboard charts)
├── numpy (math operations)
└── pyyaml (config parsing)

requirements-dev.txt
├── pytest (test runner)
├── pytest-cov (coverage)
├── mypy (type checking)
├── coverage (coverage measurement)
├── black (formatter)
├── isort (import sorter)
└── flake8 (linter)
```

All dependencies are available via PyPI. No system-level dependencies required.
