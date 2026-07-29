# Configuration

## YAML Config Reference

Full YAML configuration schema:

```yaml
source:
  type: csv | huggingface | synthetic
  path: data.csv               # file path or dataset name
  dataset: mmlu                # HF dataset name
  split: test                  # HF split
  input_column: question       # column for input text
  expected_column: answer      # column for expected output
  config: abstract_algebra     # HF config/subset
  limit: 50                    # max examples

model:
  type: openai
  model_id: gpt-4o
  api_key: sk-...              # optional, uses OPENAI_API_KEY env var
  base_url: https://...        # optional, for proxies/alternate endpoints
  temperature: 0.0
  max_tokens: 1024

task:
  type: text-generation | classification
  instruction: "Answer concisely:"
  labels: ["A", "B", "C", "D"]  # classification only

metrics:
  - type: exact-match
  - type: contains

concurrency: 10                # for async runner
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key (if not in config) |
