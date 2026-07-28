from model_eval_harness.metrics.base import MetricScore
from model_eval_harness.metrics.basic import Contains, ExactMatch
from model_eval_harness.sources.base import EvalExample
from model_eval_harness.tasks.base import TaskResult


def test_exact_match_matching() -> None:
    metric = ExactMatch()
    result = TaskResult(
        example=EvalExample(input="hello", expected="world"),
        output="world",
        latency_ms=10.0,
    )
    score = metric.compute(result)
    assert score.value == 1.0
    assert score.name == "exact_match"


def test_exact_match_non_matching() -> None:
    metric = ExactMatch()
    result = TaskResult(
        example=EvalExample(input="hello", expected="world"),
        output="earth",
    )
    score = metric.compute(result)
    assert score.value == 0.0


def test_exact_match_whitespace() -> None:
    metric = ExactMatch()
    result = TaskResult(
        example=EvalExample(input="hello", expected="  world  "),
        output="world",
    )
    score = metric.compute(result)
    assert score.value == 1.0


def test_exact_match_empty_expected() -> None:
    metric = ExactMatch()
    result = TaskResult(
        example=EvalExample(input="hello"),
        output="anything",
    )
    score = metric.compute(result)
    assert score.value == 1.0


def test_exact_match_aggregate() -> None:
    metric = ExactMatch()
    scores = [
        MetricScore(name="exact_match", value=1.0),
        MetricScore(name="exact_match", value=1.0),
        MetricScore(name="exact_match", value=0.0),
        MetricScore(name="exact_match", value=0.0),
    ]
    agg = metric.aggregate(scores)
    assert agg.value == 0.5
    assert agg.metadata["count"] == 4


def test_exact_match_aggregate_empty() -> None:
    metric = ExactMatch()
    agg = metric.aggregate([])
    assert agg.value == 0.0


def test_contains_matching() -> None:
    metric = Contains()
    result = TaskResult(
        example=EvalExample(input="hello", expected="world"),
        output="hello world today",
    )
    score = metric.compute(result)
    assert score.value == 1.0


def test_contains_non_matching() -> None:
    metric = Contains()
    result = TaskResult(
        example=EvalExample(input="hello", expected="world"),
        output="goodbye earth",
    )
    score = metric.compute(result)
    assert score.value == 0.0


def test_contains_case_insensitive() -> None:
    metric = Contains()
    result = TaskResult(
        example=EvalExample(input="hello", expected="WORLD"),
        output="hello world!",
    )
    score = metric.compute(result)
    assert score.value == 1.0


def test_contains_empty_expected() -> None:
    metric = Contains()
    result = TaskResult(
        example=EvalExample(input="hello"),
        output="anything",
    )
    score = metric.compute(result)
    assert score.value == 1.0
