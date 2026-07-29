from typing import Any

from model_eval_harness import (
    EvalExample,
    Harness,
    HarnessResult,
    Metric,
    MetricScore,
    Model,
    Source,
    Task,
    TaskResult,
)


class FakeSource(Source):
    def __init__(self, examples: list[EvalExample] | None = None) -> None:
        self._examples = examples or [
            EvalExample(input="hello", expected="world"),
            EvalExample(input="foo", expected="bar"),
        ]

    def load(self) -> Any:
        yield from self._examples

    def __len__(self) -> int:
        return len(self._examples)


class FakeModel(Model):
    model_id = "fake"

    def generate(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        return "fake output"

    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        return "fake output"


class FakeTask(Task):
    def build_prompt(self, example: EvalExample) -> str:
        return example.input

    def post_process(self, output: str, example: EvalExample) -> str:
        return output.strip()

    def run(self, example: EvalExample, model: Any) -> TaskResult:
        output = model.generate(example.input)
        return TaskResult(example=example, output=output, latency_ms=42.0)


class ExactMatch(Metric):
    def compute(self, result: TaskResult) -> MetricScore:
        match = result.output == result.example.expected
        return MetricScore(name="exact_match", value=1.0 if match else 0.0)

    def aggregate(self, scores: list[MetricScore]) -> MetricScore:
        avg = sum(s.value for s in scores) / len(scores)
        return MetricScore(name="exact_match", value=avg, metadata={"count": len(scores)})


def test_harness_runs() -> None:
    source = FakeSource()
    task = FakeTask()
    model = FakeModel()
    metric = ExactMatch()

    harness = Harness(source=source, task=task, model=model, metrics=[metric])
    result = harness.run()

    assert isinstance(result, HarnessResult)
    assert result.total_examples == 2
    assert "ExactMatch" in result.metric_scores
    assert 0.0 <= result.metric_scores["ExactMatch"].value <= 1.0
    assert result.total_latency_ms > 0


def test_source_len() -> None:
    source = FakeSource()
    assert len(source) == 2


def test_metric_aggregate() -> None:
    metric = ExactMatch()
    scores = [
        MetricScore(name="exact_match", value=1.0),
        MetricScore(name="exact_match", value=0.0),
    ]
    agg = metric.aggregate(scores)
    assert agg.value == 0.5


def test_harness_passed() -> None:
    source = FakeSource()
    task = FakeTask()
    model = FakeModel()
    metric = ExactMatch()

    harness = Harness(source=source, task=task, model=model, metrics=[metric])
    result = harness.run()

    assert isinstance(result.passed(threshold=0.0), bool)


def test_harness_fails_threshold() -> None:
    source = FakeSource(examples=[EvalExample(input="hi", expected="hello")])
    task = FakeTask()
    model = FakeModel()
    metric = ExactMatch()

    harness = Harness(source=source, task=task, model=model, metrics=[metric])
    result = harness.run()
    assert result.passed(threshold=1.0) is False


def test_harness_no_metrics() -> None:
    source = FakeSource(examples=[EvalExample(input="a", expected="b")])
    task = FakeTask()
    model = FakeModel()

    harness = Harness(source=source, task=task, model=model)
    result = harness.run()
    assert result.passed() is False
