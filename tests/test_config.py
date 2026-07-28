import tempfile
from pathlib import Path

from model_eval_harness.config import EvalConfig


def test_config_from_yaml_minimal() -> None:
    yaml_content = """
source:
  type: csv
  path: data.csv
  input_column: question
model:
  type: openai
  model_id: gpt-4o
task:
  type: text-generation
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        path = f.name

    cfg = EvalConfig.from_yaml(path)
    assert cfg.source.type == "csv"
    assert cfg.source.path == "data.csv"
    assert cfg.model.model_id == "gpt-4o"
    assert cfg.task.type == "text-generation"
    assert cfg.metrics == []
    assert cfg.concurrency == 1

    Path(path).unlink()


def test_config_from_yaml_full() -> None:
    yaml_content = """
source:
  type: huggingface
  dataset: mmlu
  split: test
  input_column: question
  expected_column: answer
  config: abstract_algebra
  limit: 50
model:
  type: openai
  model_id: gpt-4o-mini
  temperature: 0.3
  max_tokens: 512
task:
  type: classification
  instruction: "Classify the following:"
  labels: ["A", "B", "C", "D"]
metrics:
  - type: exact-match
  - type: contains
concurrency: 5
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        path = f.name

    cfg = EvalConfig.from_yaml(path)
    assert cfg.source.type == "huggingface"
    assert cfg.source.dataset == "mmlu"
    assert cfg.source.config == "abstract_algebra"
    assert cfg.source.limit == 50
    assert cfg.model.temperature == 0.3
    assert cfg.model.max_tokens == 512
    assert cfg.task.instruction == "Classify the following:"
    assert cfg.task.labels == ["A", "B", "C", "D"]
    assert len(cfg.metrics) == 2
    assert cfg.metrics[0].type == "exact-match"
    assert cfg.metrics[1].type == "contains"
    assert cfg.concurrency == 5

    Path(path).unlink()
