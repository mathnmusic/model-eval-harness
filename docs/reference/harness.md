# Harness API

The `Harness` is the orchestrator that connects sources, tasks, models, and metrics.

## Basic Usage

```python
from model_eval_harness import Harness

harness = Harness(
    source=my_source,
    task=my_task,
    model=my_model,
    metrics=[my_metric],
)

result = harness.run()
result.print_report()
```

## HarnessResult

```python
@dataclass
class HarnessResult:
    task_results: list[TaskResult]
    metric_scores: dict[str, MetricScore]
    total_examples: int
    total_latency_ms: float

    def passed(self, threshold: float = 0.5) -> bool:
        """True if all metrics >= threshold."""

    def print_report(self) -> None:
        """Pretty-print results table via Rich."""
```

## Async Runner

```python
import asyncio

result = asyncio.run(harness.run_async(concurrency=10))
```

## Programmatic Access

```python
result = harness.run()

# Per-example results
for task_result in result.task_results:
    print(f"{task_result.example.input} → {task_result.output}")
    print(f"  latency: {task_result.latency_ms:.0f}ms")

# Aggregate scores
for name, score in result.metric_scores.items():
    print(f"{name}: {score.value:.4f}")

# CI pass/fail
if result.passed(threshold=0.8):
    print("PASSED")
else:
    print("FAILED")
    exit(1)
```
