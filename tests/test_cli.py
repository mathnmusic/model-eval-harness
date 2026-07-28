import csv
import tempfile
from pathlib import Path

from click.testing import CliRunner

from model_eval_harness.cli import main


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "model-eval-harness" in result.output


def test_cli_version() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_list_sources() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list-sources"])
    assert result.exit_code == 0
    assert "huggingface" in result.output
    assert "csv" in result.output
    assert "synthetic" in result.output


def test_list_tasks() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["list-tasks"])
    assert result.exit_code == 0
    assert "text-generation" in result.output
    assert "classification" in result.output


def test_quick_missing_source_path() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["quick", "--source-type", "csv"])
    assert result.exit_code != 0


def test_quick_csv_source() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerow({"question": "2+2", "answer": "4"})
        writer.writerow({"question": "3+3", "answer": "6"})
        path = f.name

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "quick",
            "--source-type",
            "csv",
            "--source-path",
            path,
            "--input-column",
            "question",
            "--expected-column",
            "answer",
            "--metric",
            "exact-match",
        ],
        env={"OPENAI_API_KEY": "sk-test"},
    )
    # Fails on API call, but CLI parsing succeeded (exit code != 2 = usage error)
    assert result.exit_code != 2
    Path(path).unlink()


def test_quick_synthetic_source() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "quick",
            "--source-type",
            "synthetic",
            "--source-path",
            "test math problems",
            "--limit",
            "3",
            "--metric",
            "contains",
        ],
        env={"OPENAI_API_KEY": "sk-test"},
    )
    # Fails due to fake API key, but CLI parsing succeeds (no click.UsageError)
    assert result.exit_code != 2  # 2 = click usage error


def test_run_yaml_config_parses() -> None:
    csv_path = ""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["prompt"])
        writer.writeheader()
        writer.writerow({"prompt": "Hello"})
        csv_path = f.name

    yaml_content = f"""source:
  type: csv
  path: {csv_path}
  input_column: prompt
model:
  type: openai
  model_id: gpt-4o
task:
  type: text-generation
metrics:
  - type: exact-match
concurrency: 1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    runner = CliRunner()
    result = runner.invoke(main, ["run", yaml_path], env={"OPENAI_API_KEY": "sk-test"})
    # Config parsed OK, fails on API call — not a click error
    assert result.exit_code != 2

    Path(yaml_path).unlink()
    Path(csv_path).unlink()


def test_run_missing_config() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["run", "nonexistent.yaml"])
    assert result.exit_code != 0
