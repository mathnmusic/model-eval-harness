from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class SourceConfig(BaseModel):
    type: str = "csv"
    path: str = ""
    dataset: str = ""
    split: str = "test"
    input_column: str = "question"
    expected_column: str | None = "answer"
    config: str | None = None
    limit: int | None = None


class ModelConfig(BaseModel):
    type: str = "openai"
    model_id: str = "gpt-4o"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.0
    max_tokens: int = 1024


class TaskConfig(BaseModel):
    type: str = "text-generation"
    instruction: str = ""
    labels: list[str] | None = None


class MetricConfig(BaseModel):
    type: str = "exact-match"


class EvalConfig(BaseModel):
    source: SourceConfig
    model: ModelConfig
    task: TaskConfig
    metrics: list[MetricConfig] = []
    concurrency: int = 1
    output: str | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "EvalConfig":
        with open(path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return cls.model_validate(data)
