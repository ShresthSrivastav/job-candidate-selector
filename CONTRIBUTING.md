# Contributing to RedRobe

## Development Setup

1. Fork and clone the repository
2. Install dependencies: `make install`
3. Install pre-commit hooks: `pre-commit install`
4. Create a feature branch: `git checkout -b feature/my-feature`

## Code Standards

- Format with black (line-length=100): `make format`
- Lint with flake8: `make lint`
- All tests must pass: `make test`
- Coverage must not decrease: `make coverage`

## Pull Request Process

1. Update tests for any new functionality
2. Update documentation for any changed behavior
3. Run the full test suite: `make test-full`
4. Submit PR with descriptive title and context

## Commit Messages

Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `ci:`, `chore:`

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
