# Metrics

Metrics score model outputs against expected values.

## MetricScore

```python
@dataclass
class MetricScore:
    name: str
    value: float          # 0.0 to 1.0
    metadata: dict[str, Any]
```

## Built-in Metrics

### ExactMatch

Returns 1.0 if output matches expected exactly (whitespace-insensitive).

```python
from model_eval_harness.metrics import ExactMatch
```

### Contains

Returns 1.0 if output contains the expected string (case-insensitive).

```python
from model_eval_harness.metrics import Contains
```

## Custom Metrics

Implement the `Metric` abstract class:

```python
from model_eval_harness.metrics.base import Metric, MetricScore

class F1Score(Metric):
    def compute(self, result):
        # per-example scoring
        return MetricScore(name="f1", value=calculate_f1(result))

    def aggregate(self, scores):
        avg = sum(s.value for s in scores) / len(scores)
        return MetricScore(name="f1", value=avg, metadata={"count": len(scores)})
```
