# CLI Usage

## Commands

### `meh quick`

Quick evaluation without a config file.

```bash
meh quick [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--source-type`, `-s` | (required) | `csv`, `huggingface`, `synthetic` |
| `--source-path`, `-d` | (required) | File path or dataset name |
| `--input-column` | `question` | Column for input text |
| `--expected-column` | `answer` | Column for expected output |
| `--split` | `test` | HF dataset split |
| `--limit` | (none) | Max examples |
| `--model`, `-m` | `gpt-4o` | OpenAI model ID |
| `--task-type`, `-t` | `text-generation` | `text-generation` or `classification` |
| `--metric` | (all) | Can repeat: `exact-match`, `contains` |
| `--api-key` | `$OPENAI_API_KEY` | OpenAI API key |
| `--async-run` | off | Run with async concurrency |

### `meh run`

Run from a YAML config file.

```bash
meh run eval.yaml [--async-run]
```

### `meh list-sources`

List available data source types.

### `meh list-tasks`

List available task types.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All metrics passed threshold (default: 0.5) |
| 1 | One or more metrics below threshold |
| 2 | Usage error (bad arguments) |
