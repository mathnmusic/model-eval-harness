"""CLI entry point for model-eval-harness."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def main():
    """model-eval-harness — connect testing data sources to LLM evaluations."""


@main.command()
@click.argument("config", type=click.Path(exists=True))
def run(config: str):
    """Run an evaluation from a YAML config file."""
    console.print(f"[bold]Running eval from[/bold] {config}")
    console.print("[yellow]Not yet implemented[/yellow]")


@main.command()
@click.option("--source", "-s", help="Source name or path")
@click.option("--model", "-m", default="gpt-4o", help="Model to evaluate")
@click.option("--task", "-t", default="default", help="Task type")
def quick(source: str, model: str, task: str):
    """Quick evaluation without a config file."""
    console.print(f"[bold]Quick eval:[/bold] source={source}, model={model}, task={task}")
    console.print("[yellow]Not yet implemented[/yellow]")


@main.command()
def list_sources():
    """List available data sources."""
    console.print("[yellow]Not yet implemented[/yellow]")


@main.command()
def list_tasks():
    """List available task types."""
    console.print("[yellow]Not yet implemented[/yellow]")


if __name__ == "__main__":
    main()
