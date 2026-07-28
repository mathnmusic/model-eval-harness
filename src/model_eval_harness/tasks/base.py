from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..sources.base import EvalExample


@dataclass
class TaskResult:
    example: EvalExample
    output: str
    raw_response: Any = None
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class Task(ABC):
    @abstractmethod
    def build_prompt(self, example: EvalExample) -> str | list[dict[str, str]]: ...

    @abstractmethod
    def post_process(self, output: str, example: EvalExample) -> str: ...

    @abstractmethod
    def run(self, example: EvalExample, model: Any) -> TaskResult: ...
