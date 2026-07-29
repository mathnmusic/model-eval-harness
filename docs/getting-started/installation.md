# Installation

## Requirements

- Python 3.12+
- Optional: OpenAI API key for model evaluation

## Install with uv (recommended)

```bash
uv add model-eval-harness
```

## Install with pip

```bash
pip install model-eval-harness
```

## From source

```bash
git clone https://github.com/mathnmusic/model-eval-harness
cd model-eval-harness
uv sync
uv run meh --help
```

## Verify

```bash
meh --version
meh list-sources
```
