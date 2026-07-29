# YAML Configuration

YAML configs make evaluations reproducible and version-controlled. Define your source, model, task, and metrics in a single file.

## Examples

### CSV evaluation

```yaml
source:
  type: csv
  path: ./data/test_questions.csv
  input_column: prompt
  expected_column: ground_truth
model:
  type: openai
  model_id: gpt-4o-mini
  temperature: 0.0
task:
  type: text-generation
metrics:
  - type: exact-match
  - type: contains
```

### HuggingFace benchmark

```yaml
source:
  type: huggingface
  dataset: mmlu
  config: high_school_mathematics
  split: test
  input_column: question
  expected_column: answer
  limit: 100
model:
  type: openai
  model_id: gpt-4o
task:
  type: classification
  labels: ["A", "B", "C", "D"]
  instruction: "Choose the correct answer."
metrics:
  - type: exact-match
concurrency: 10
```

### Synthetic test generation

```yaml
source:
  type: synthetic
  spec: "customer support queries about refund policies"
  limit: 50
model:
  type: openai
  model_id: gpt-4o
task:
  type: text-generation
  instruction: "You are a helpful customer support agent."
metrics:
  - type: contains
```

## Validation

Configs are validated against a Pydantic schema at load time. Invalid configs fail immediately with a clear error message.
