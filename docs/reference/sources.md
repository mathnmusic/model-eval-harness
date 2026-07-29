# Sources

Sources provide test examples to the harness. Every source yields `EvalExample` objects.

## EvalExample

```python
@dataclass
class EvalExample:
    input: str
    expected: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

## Built-in Sources

### CSVSource

Load examples from a CSV file.

```python
from model_eval_harness.sources import CSVSource

source = CSVSource(
    path="questions.csv",
    input_column="question",
    expected_column="answer",
    limit=50,
)
```

### HuggingFaceSource

Load examples from any HuggingFace dataset.

```python
from model_eval_harness.sources import HuggingFaceSource

source = HuggingFaceSource(
    dataset_name="mmlu",
    split="test",
    input_column="question",
    expected_column="answer",
    config="abstract_algebra",
    limit=20,
)
```

### SyntheticSource

Generate test examples from a specification using an LLM.

```python
from model_eval_harness.sources import SyntheticSource
from model_eval_harness.models import OpenAIModel

source = SyntheticSource(
    spec="elementary math word problems with numeric answers",
    count=20,
    model=OpenAIModel("gpt-4o"),
)
```

Without a model, SyntheticSource generates placeholder examples.

## Custom Sources

Implement the `Source` abstract class:

```python
from model_eval_harness.sources.base import Source, EvalExample

class MySource(Source):
    def load(self):
        for item in my_data:
            yield EvalExample(
                input=item["text"],
                expected=item["label"],
                metadata={"id": item["id"]},
            )

    def __len__(self):
        return len(my_data)
```
