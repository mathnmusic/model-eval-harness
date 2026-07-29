# Tasks

Tasks define how prompts are built and outputs are processed.

## TextGenerationTask

Simple text-in, text-out evaluation.

```python
from model_eval_harness.tasks import TextGenerationTask

task = TextGenerationTask(instruction="Answer concisely:")
```

Prompts are built as: `{instruction}\n\n{input}`

## ClassificationTask

Multi-class classification with label-aware prompting.

```python
from model_eval_harness.tasks import ClassificationTask

task = ClassificationTask(
    labels=["positive", "negative", "neutral"],
    instruction="Classify the sentiment:",
)
```

Prompts include the label set and instructions to output only the category name.

## Custom Tasks

Implement the `Task` abstract class:

```python
from model_eval_harness.tasks.base import Task, TaskResult

class MyTask(Task):
    def build_prompt(self, example):
        return f"Question: {example.input}\nAnswer:"

    def post_process(self, output, example):
        return output.strip()

    def run(self, example, model):
        prompt = self.build_prompt(example)
        start = time.perf_counter()
        output = model.generate(prompt)
        latency = (time.perf_counter() - start) * 1000
        return TaskResult(
            example=example,
            output=self.post_process(output, example),
            latency_ms=latency,
        )
```
