"""CLI entry point for model-eval-harness."""

import asyncio
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from .config import EvalConfig
from .harness import Harness
from .metrics.base import Metric
from .metrics.basic import Contains, ExactMatch
from .models.openai import OpenAIModel
from .sources.base import Source
from .sources.csv_source import CSVSource
from .sources.huggingface import HuggingFaceSource
from .sources.synthetic import SyntheticSource
from .tasks.basic import ClassificationTask, TextGenerationTask

console = Console()

SOURCES = {"huggingface": HuggingFaceSource, "csv": CSVSource, "synthetic": SyntheticSource}
TASKS = {"text-generation": TextGenerationTask, "classification": ClassificationTask}
METRICS = {"exact-match": ExactMatch, "contains": Contains}


def _build_source(cfg: Any) -> Source:
    source_type = getattr(cfg, "type", "csv")
    if source_type == "huggingface":
        return HuggingFaceSource(
            dataset_name=cfg.dataset or cfg.path,
            split=getattr(cfg, "split", "test"),
            input_column=getattr(cfg, "input_column", "question"),
            expected_column=getattr(cfg, "expected_column", "answer"),
            config=getattr(cfg, "config", None),
            limit=getattr(cfg, "limit", None),
        )
    elif source_type == "csv":
        return CSVSource(
            path=cfg.path,
            input_column=cfg.input_column,
            expected_column=getattr(cfg, "expected_column", None),
            limit=getattr(cfg, "limit", None),
        )
    elif source_type == "synthetic":
        return SyntheticSource(
            spec=getattr(cfg, "spec", cfg.path),
            count=getattr(cfg, "limit", 10) or 10,
        )
    raise ValueError(f"Unknown source type: {source_type}")


def _build_model(cfg: Any) -> OpenAIModel:
    return OpenAIModel(
        model_id=getattr(cfg, "model_id", "gpt-4o"),
        api_key=getattr(cfg, "api_key", None),
        base_url=getattr(cfg, "base_url", None),
        temperature=getattr(cfg, "temperature", 0.0),
        max_tokens=getattr(cfg, "max_tokens", 1024),
    )


def _build_task(cfg: Any) -> TextGenerationTask | ClassificationTask:
    task_type = getattr(cfg, "type", "text-generation")
    if task_type == "classification":
        return ClassificationTask(
            labels=getattr(cfg, "labels", None),
            instruction=getattr(cfg, "instruction", ""),
        )
    return TextGenerationTask(instruction=getattr(cfg, "instruction", ""))


def _build_metrics(cfg_metrics: list[Any]) -> list[Metric]:
    result: list[Metric] = []
    for m in cfg_metrics:
        name = getattr(m, "type", "exact-match")
        if name in METRICS:
            result.append(METRICS[name]())
    return result or [ExactMatch(), Contains()]


def _run_and_report(harness: Harness) -> None:
    with console.status("[bold green]Running evaluation..."):
        result = harness.run()

    result.print_report()

    threshold = 0.5
    if result.passed(threshold):
        console.print(f"[green]PASSED[/green] (threshold: {threshold})")
    else:
        console.print(f"[red]FAILED[/red] (threshold: {threshold})")
        raise SystemExit(1)


@click.group()
@click.version_option()
def main() -> None:
    """model-eval-harness -- connect testing data sources to LLM evaluations."""


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--async/--no-async", default=False, help="Run with async concurrency")
def run(config: str, async_: bool) -> None:
    """Run an evaluation from a YAML config file."""
    cfg = EvalConfig.from_yaml(config)

    source = _build_source(cfg.source)
    task = _build_task(cfg.task)
    model = _build_model(cfg.model)
    metrics = _build_metrics(cfg.metrics)

    harness = Harness(source=source, task=task, model=model, metrics=metrics)

    if async_:
        with console.status("[bold green]Running evaluation (async)..."):
            result = asyncio.run(harness.run_async(concurrency=cfg.concurrency or 10))
        result.print_report()
        threshold = 0.5
        if result.passed(threshold):
            console.print(f"[green]PASSED[/green] (threshold: {threshold})")
        else:
            console.print(f"[red]FAILED[/red] (threshold: {threshold})")
            raise SystemExit(1)
    else:
        _run_and_report(harness)


@main.command()
@click.option("--source-type", "-s", type=click.Choice(SOURCES.keys()), required=True)
@click.option("--source-path", "-d", help="Dataset name (HF) or file path (CSV)")
@click.option("--input-column", default="question", help="Column name for input text")
@click.option("--expected-column", default="answer", help="Column name for expected output")
@click.option("--split", default="test", help="Dataset split (HF only)")
@click.option("--limit", type=int, help="Limit number of examples")
@click.option("--model", "-m", default="gpt-4o", help="OpenAI model ID")
@click.option("--task-type", "-t", type=click.Choice(TASKS.keys()), default="text-generation")
@click.option("--metric", type=click.Choice(METRICS.keys()), multiple=True)
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
@click.option("--async/--no-async", default=False, help="Run with async concurrency")
def quick(
    source_type: str,
    source_path: str | None,
    input_column: str,
    expected_column: str,
    split: str,
    limit: int | None,
    model: str,
    task_type: str,
    metric: tuple[str, ...],
    api_key: str | None,
    async_: bool,
) -> None:
    """Quick evaluation from the command line."""
    if not source_path:
        raise click.UsageError("--source-path is required")

    source: Source
    if source_type == "huggingface":
        source = HuggingFaceSource(
            dataset_name=source_path,
            split=split,
            input_column=input_column,
            expected_column=expected_column,
            limit=limit,
        )
    elif source_type == "csv":
        source = CSVSource(
            path=source_path,
            input_column=input_column,
            expected_column=expected_column,
            limit=limit,
        )
    elif source_type == "synthetic":
        source = SyntheticSource(
            spec=source_path,
            count=limit or 10,
        )
    else:
        raise click.BadParameter(f"Unknown source type: {source_type}")

    task_cls = TASKS[task_type]
    task = task_cls()

    model_instance = OpenAIModel(model_id=model, api_key=api_key)

    chosen_metrics = [METRICS[m]() for m in metric] if metric else [ExactMatch(), Contains()]

    harness = Harness(source=source, task=task, model=model_instance, metrics=chosen_metrics)

    if async_:
        with console.status("[bold green]Running evaluation (async)..."):
            result = asyncio.run(harness.run_async())
        result.print_report()
        threshold = 0.5
        if result.passed(threshold):
            console.print(f"[green]PASSED[/green] (threshold: {threshold})")
        else:
            console.print(f"[red]FAILED[/red] (threshold: {threshold})")
            raise SystemExit(1)
    else:
        _run_and_report(harness)


@main.command()
def list_sources() -> None:
    """List available data sources."""
    table = Table(title="Available Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    for name, cls in SOURCES.items():
        table.add_row(name, cls.__name__)
    console.print(table)


@main.command()
def list_tasks() -> None:
    """List available task types."""
    table = Table(title="Available Tasks")
    table.add_column("Name", style="cyan")
    table.add_column("Class", style="green")
    for name, cls in TASKS.items():
        table.add_row(name, cls.__name__)
    console.print(table)


if __name__ == "__main__":
    main()
