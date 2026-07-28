from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..tasks.base import TaskResult


@dataclass
class MetricScore:
    name: str
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Metric(ABC):
    @abstractmethod
    def compute(self, result: TaskResult) -> MetricScore: ...

    @abstractmethod
    def aggregate(self, scores: list[MetricScore]) -> MetricScore: ...
