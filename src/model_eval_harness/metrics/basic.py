from ..tasks.base import TaskResult
from .base import Metric, MetricScore


class ExactMatch(Metric):
    def compute(self, result: TaskResult) -> MetricScore:
        expected = result.example.expected or ""
        match = result.output.strip() == expected.strip()
        return MetricScore(name="exact_match", value=1.0 if match else 0.0)

    def aggregate(self, scores: list[MetricScore]) -> MetricScore:
        avg = sum(s.value for s in scores) / len(scores) if scores else 0.0
        return MetricScore(name="exact_match", value=avg, metadata={"count": len(scores)})


class Contains(Metric):
    def compute(self, result: TaskResult) -> MetricScore:
        expected = result.example.expected or ""
        match = expected.lower() in result.output.lower()
        return MetricScore(name="contains", value=1.0 if match else 0.0)

    def aggregate(self, scores: list[MetricScore]) -> MetricScore:
        avg = sum(s.value for s in scores) / len(scores) if scores else 0.0
        return MetricScore(name="contains", value=avg, metadata={"count": len(scores)})
