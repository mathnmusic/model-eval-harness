# Quick Start

## Evaluate a CSV file

```bash
meh quick \
  --source-type csv \
  --source-path data.csv \
  --input-column question \
  --expected-column answer \
  --model gpt-4o \
  --metric exact-match \
  --metric contains
```

## Evaluate a HuggingFace dataset

```bash
meh quick \
  --source-type huggingface \
  --source-path mmlu \
  --split test \
  --input-column question \
  --expected-column answer \
  --config abstract_algebra \
  --limit 20 \
  --model gpt-4o-mini \
  --task-type classification
```

## Generate synthetic test data

```bash
meh quick \
  --source-type synthetic \
  --source-path "elementary math problems with numeric answers" \
  --limit 10 \
  --model gpt-4o
```

## Use a YAML config

```yaml
# eval.yaml
source:
  type: csv
  path: questions.csv
  input_column: question
  expected_column: answer
model:
  type: openai
  model_id: gpt-4o
task:
  type: text-generation
metrics:
  - type: exact-match
  - type: contains
concurrency: 5
```

```bash
meh run eval.yaml --async-run
```
