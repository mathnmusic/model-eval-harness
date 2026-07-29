# AGENTS.md

This file provides guidance to AI coding agents working on this repository.

## Project Overview

`model-eval-harness` is a Python framework for connecting testing data sources to LLM evaluations. Architecture: `Source → Task → Model → Metrics → Harness`.

## Development Commands

```bash
uv sync                    # install all dependencies
uv run meh --help          # CLI usage
uv run pytest              # run tests
uv run mypy src/           # type check (strict mode)
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
uv run mkdocs serve         # preview docs
```

## Code Style

- Python 3.12+, strict mypy typing
- Ruff for linting and formatting (line length 100, double quotes)
- Pydantic for configuration models
- Abstract base classes for extension points

## Architecture

```
src/model_eval_harness/
├── sources/     # Data sources (CSV, HuggingFace, Synthetic)
├── models/      # Model interfaces (OpenAI)
├── tasks/       # Task types (TextGeneration, Classification)
├── metrics/     # Scoring (ExactMatch, Contains)
├── harness.py   # Orchestrator
├── config.py    # YAML config (Pydantic)
└── cli.py       # Click CLI
```

## CI

- Lint & Format (ruff)
- Type Check (mypy strict)
- Tests (pytest, >80% coverage, py3.12 + py3.13)
- Security Scan (pip-audit)
- Build Check (uv build)
- Docs Deploy (GitHub Pages via mkdocs)

## Adding Features

Follow the pattern in `docs/contributing.md`. Every new source/model/task/metric must include: implementation, tests, CLI registration, and documentation.
