"""CLI entry point for model-eval-harness."""

import click
from rich.console import Console
from rich.table import Table

from .harness import Harness
from .metrics.basic import Contains, ExactMatch
from .models.openai import OpenAIModel
from .sources.base import Source
from .sources.csv_source import CSVSource
from .sources.huggingface import HuggingFaceSource
from .tasks.basic import ClassificationTask, TextGenerationTask

console = Console()

SOURCES = {"huggingface": HuggingFaceSource, "csv": CSVSource}
TASKS = {"text-generation": TextGenerationTask, "classification": ClassificationTask}
METRICS = {"exact-match": ExactMatch, "contains": Contains}


@click.group()
@click.version_option()
def main() -> None:
    """model-eval-harness -- connect testing data sources to LLM evaluations."""


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
    else:
        raise click.BadParameter(f"Unknown source type: {source_type}")

    task_cls = TASKS[task_type]
    task = task_cls()

    model_instance = OpenAIModel(model_id=model, api_key=api_key)

    chosen_metrics = [METRICS[m]() for m in metric] if metric else [ExactMatch(), Contains()]

    harness = Harness(source=source, task=task, model=model_instance, metrics=chosen_metrics)

    with console.status("[bold green]Running evaluation..."):
        result = harness.run()

    result.print_report()

    threshold = 0.5
    if result.passed(threshold):
        console.print(f"[green]PASSED[/green] (threshold: {threshold})")
    else:
        console.print(f"[red]FAILED[/red] (threshold: {threshold})")
        raise SystemExit(1)


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
