from dataclasses import dataclass

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from .metrics.base import Metric, MetricScore
from .models.base import Model
from .sources.base import EvalExample, Source
from .tasks.base import Task, TaskResult


@dataclass
class HarnessResult:
    task_results: list[TaskResult]
    metric_scores: dict[str, MetricScore]
    total_examples: int
    total_latency_ms: float

    def passed(self, threshold: float = 0.5) -> bool:
        scores = [s.value for s in self.metric_scores.values()]
        return all(s >= threshold for s in scores) if scores else False

    def print_report(self) -> None:
        console = Console()
        table = Table(title="Evaluation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Details", style="dim")
        for name, score in self.metric_scores.items():
            table.add_row(name, f"{score.value:.4f}", str(score.metadata))
        table.add_row("Examples", str(self.total_examples), "")
        table.add_row("Total Latency", f"{self.total_latency_ms:.0f}ms", "")
        console.print(table)


class Harness:
    def __init__(
        self,
        source: Source,
        task: Task,
        model: Model,
        metrics: list[Metric] | None = None,
    ):
        self.source = source
        self.task = task
        self.model = model
        self.metrics = metrics or []

    def run(self) -> HarnessResult:
        results: list[TaskResult] = []
        examples = list(self.source.load())

        with Progress() as progress:
            task_id = progress.add_task("Running eval...", total=len(examples))
            for example in examples:
                result = self.task.run(example, self.model)
                results.append(result)
                progress.advance(task_id)

        return self._build_result(results)

    async def run_async(self, concurrency: int = 10) -> HarnessResult:
        import asyncio

        examples = list(self.source.load())
        semaphore = asyncio.Semaphore(concurrency)

        async def run_one(example: EvalExample) -> TaskResult:
            async with semaphore:
                return await self._run_example_async(example)

        results = await asyncio.gather(*[run_one(e) for e in examples])
        return self._build_result(list(results))

    async def _run_example_async(self, example: EvalExample) -> TaskResult:
        prompt = self.task.build_prompt(example)
        import time

        start = time.perf_counter()
        output = await self.model.generate_async(prompt)
        latency = (time.perf_counter() - start) * 1000
        processed = self.task.post_process(output, example)
        return TaskResult(
            example=example,
            output=processed,
            raw_response=output,
            latency_ms=latency,
        )

    def _build_result(self, results: list[TaskResult]) -> HarnessResult:
        metric_scores: dict[str, MetricScore] = {}
        for metric in self.metrics:
            scores = [metric.compute(r) for r in results]
            metric_scores[metric.__class__.__name__] = metric.aggregate(scores)

        total_latency = sum(r.latency_ms for r in results)
        return HarnessResult(
            task_results=results,
            metric_scores=metric_scores,
            total_examples=len(results),
            total_latency_ms=total_latency,
        )
