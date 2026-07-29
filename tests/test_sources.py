import csv
import tempfile
from pathlib import Path

from model_eval_harness.sources.base import EvalExample
from model_eval_harness.sources.csv_source import CSVSource
from model_eval_harness.sources.synthetic import SyntheticSource


def test_csv_source_loads_all_rows() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerow({"question": "What is 2+2?", "answer": "4"})
        writer.writerow({"question": "Capital of France?", "answer": "Paris"})
        path = f.name

    source = CSVSource(path=path, input_column="question", expected_column="answer")
    examples = list(source.load())

    assert len(source) == 2
    assert len(examples) == 2
    assert examples[0].input == "What is 2+2?"
    assert examples[0].expected == "4"
    assert examples[1].input == "Capital of France?"
    assert examples[1].expected == "Paris"

    Path(path).unlink()


def test_csv_source_limit() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text"])
        writer.writeheader()
        for i in range(10):
            writer.writerow({"text": f"Row {i}"})
        path = f.name

    source = CSVSource(path=path, input_column="text", limit=3)
    assert len(source) == 3
    assert len(list(source.load())) == 3

    Path(path).unlink()


def test_csv_source_no_expected() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["prompt"])
        writer.writeheader()
        writer.writerow({"prompt": "Hello"})
        path = f.name

    source = CSVSource(path=path, input_column="prompt")
    examples = list(source.load())
    assert examples[0].expected is None

    Path(path).unlink()


def test_synthetic_source_without_model() -> None:
    source = SyntheticSource(spec="test math question", count=5)
    examples = list(source.load())

    assert len(source) == 5
    assert len(examples) == 5
    for ex in examples:
        assert "test math question" in ex.input
        assert ex.metadata["source"] == "synthetic"


def test_synthetic_source_is_idempotent() -> None:
    source = SyntheticSource(spec="test", count=3)
    first = list(source.load())
    second = list(source.load())
    assert len(first) == len(second)
    assert [e.input for e in first] == [e.input for e in second]


def test_synthetic_source_with_seed() -> None:
    seed = [EvalExample(input="seed input", expected="seed expected")]
    source = SyntheticSource(spec="test", count=3, seed_examples=seed)

    assert len(source) == 3
    examples = list(source.load())
    assert examples[0].input == "seed input"


class FakeSyntheticModel:
    def generate(self, prompt: str | list[dict[str, str]], **kwargs: object) -> str:
        return '{"input": "What is 2+2?", "expected": "4"}'

    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: object) -> str:
        return '{"input": "What is 2+2?", "expected": "4"}'


def test_synthetic_source_with_model() -> None:
    model = FakeSyntheticModel()
    source = SyntheticSource(spec="math problems", count=2, model=model)
    examples = list(source.load())

    assert len(examples) == 2
    assert examples[0].input == "What is 2+2?"
    assert examples[0].expected == "4"
    assert examples[0].metadata["source"] == "synthetic"


def test_synthetic_source_with_model_and_seed() -> None:
    model = FakeSyntheticModel()
    seed = [EvalExample(input="seed q", expected="seed a")]
    source = SyntheticSource(spec="math", count=3, model=model, seed_examples=seed)
    examples = list(source.load())

    assert len(examples) == 3
    assert examples[0].input == "seed q"
    assert examples[1].input == "What is 2+2?"
