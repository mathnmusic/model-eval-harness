# model-eval-harness

Framework for connecting testing data sources to LLM evaluations.

Stop wrangling data into benchmark formats. `model-eval-harness` lets you plug in any data source — HuggingFace datasets, CSV files, SQL databases, or LLM-generated synthetic data — and evaluate any model with any task and any metric.

## Install

```bash
pip install model-eval-harness
# or
uv add model-eval-harness
```

## Quick Start

```bash
# Evaluate GPT-4o on a CSV of questions
meh quick \
  --source-type csv \
  --source-path questions.csv \
  --model gpt-4o \
  --metric exact-match

# Or use a YAML config
meh run eval.yaml
```

## Architecture

```
Source → Task → Model → Metrics → HarnessResult
```

| Component | Role | Built-in |
|-----------|------|----------|
| **Source** | Where test data comes from | HF datasets, CSV, Synthetic |
| **Task** | How prompts are built and outputs processed | TextGeneration, Classification |
| **Model** | What generates responses | OpenAI (sync + async) |
| **Metric** | How outputs are scored | ExactMatch, Contains |
| **Harness** | Orchestrator that runs it all | Sync + async runner |

## Why model-eval-harness?

- **Data-source agnostic**: Connect anything that yields `(input, expected)` pairs
- **Model agnostic**: OpenAI built-in, extend with any API
- **CI-ready**: `meh run --async-run` exits 0/1 for pass/fail
- **Fast async**: Evaluate thousands of examples concurrently
- **YAML config**: Reproducible, version-controlled eval definitions
