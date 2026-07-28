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
    assert "source-path" in result.output.lower() or "required" in result.output.lower()


def test_run_missing_config() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["run", "nonexistent.yaml"])
    assert result.exit_code != 0
