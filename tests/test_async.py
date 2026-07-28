import asyncio
from typing import Any

from model_eval_harness.harness import Harness
from model_eval_harness.metrics.basic import ExactMatch
from model_eval_harness.models.base import Model
from model_eval_harness.sources.base import EvalExample, Source
from model_eval_harness.tasks.base import Task, TaskResult


class AsyncFakeSource(Source):
    def __init__(self, count: int = 3) -> None:
        self._examples = [
            EvalExample(input=f"test {i}", expected=f"output {i}") for i in range(count)
        ]

    def load(self) -> Any:
        yield from self._examples

    def __len__(self) -> int:
        return len(self._examples)


class AsyncFakeModel(Model):
    model_id = "fake-async"

    def generate(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        return f"sync response to: {prompt}"

    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        await asyncio.sleep(0.001)
        return f"async response to: {prompt}"


class AsyncFakeTask(Task):
    def build_prompt(self, example: EvalExample) -> str:
        return example.input

    def post_process(self, output: str, example: EvalExample) -> str:
        return output.strip()

    def run(self, example: EvalExample, model: Any) -> TaskResult:
        output = model.generate(example.input)
        return TaskResult(example=example, output=output, latency_ms=1.0)


def test_harness_async() -> None:
    source = AsyncFakeSource(count=5)
    task = AsyncFakeTask()
    model = AsyncFakeModel()
    metric = ExactMatch()

    harness = Harness(source=source, task=task, model=model, metrics=[metric])
    result = asyncio.run(harness.run_async(concurrency=3))

    assert result.total_examples == 5
    assert result.total_latency_ms > 0
    assert "ExactMatch" in result.metric_scores


def test_harness_async_passed() -> None:
    source = AsyncFakeSource(count=2)
    task = AsyncFakeTask()
    model = AsyncFakeModel()
    metric = ExactMatch()

    harness = Harness(source=source, task=task, model=model, metrics=[metric])
    result = asyncio.run(harness.run_async(concurrency=2))

    assert result.total_examples == 2
    assert result.passed(threshold=0.0) is True
