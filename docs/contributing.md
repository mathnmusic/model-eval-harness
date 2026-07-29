# Contributing

## Setup

```bash
git clone https://github.com/mathnmusic/model-eval-harness
cd model-eval-harness
uv sync
uv run pre-commit install
```

## Development

```bash
uv run meh --help
uv run pytest
uv run mypy src/
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Docs

```bash
uv run mkdocs serve    # preview at http://localhost:8000
uv run mkdocs build    # build static site
```

## CI

All PRs must pass:
- Lint & Format (ruff)
- Type Check (mypy strict)
- Tests (pytest with >80% coverage, py3.12 + py3.13)
- Security Scan (pip-audit)
- Build Check (uv build)

## Adding a Source

1. Create `src/model_eval_harness/sources/my_source.py`
2. Implement `Source.load()` and `Source.__len__()`
3. Register in `src/model_eval_harness/sources/__init__.py`
4. Add to CLI: `SOURCES` dict and quick command handler
5. Add tests in `tests/test_sources.py`
6. Add doc in `docs/reference/sources.md`

## Adding a Model

1. Create `src/model_eval_harness/models/my_model.py`
2. Implement `Model.generate()` and `Model.generate_async()`
3. Register in `src/model_eval_harness/models/__init__.py`
4. Add tests
5. Add docs

## Adding a Metric

1. Create or extend `src/model_eval_harness/metrics/`
2. Implement `Metric.compute()` and `Metric.aggregate()`
3. Register and add CLI option
4. Add tests and docs
