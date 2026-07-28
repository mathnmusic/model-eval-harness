from typing import Any

from model_eval_harness.sources.base import EvalExample
from model_eval_harness.tasks.base import TaskResult
from model_eval_harness.tasks.basic import ClassificationTask, TextGenerationTask


class FakeModel:
    def generate(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        return "test output"

    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        return "test output"


def test_text_generation_builds_prompt() -> None:
    task = TextGenerationTask()
    example = EvalExample(input="What is AI?")
    prompt = task.build_prompt(example)
    assert prompt == "What is AI?"


def test_text_generation_with_instruction() -> None:
    task = TextGenerationTask(instruction="Answer concisely:")
    example = EvalExample(input="What is AI?")
    prompt = task.build_prompt(example)
    assert "Answer concisely:" in prompt
    assert "What is AI?" in prompt


def test_text_generation_post_process() -> None:
    task = TextGenerationTask()
    example = EvalExample(input="test")
    result = task.post_process("  hello world  ", example)
    assert result == "hello world"


def test_text_generation_run() -> None:
    task = TextGenerationTask()
    model = FakeModel()
    example = EvalExample(input="What is AI?")
    result = task.run(example, model)

    assert isinstance(result, TaskResult)
    assert result.output == "test output"
    assert result.latency_ms > 0


def test_classification_builds_prompt() -> None:
    task = ClassificationTask(labels=["positive", "negative", "neutral"])
    example = EvalExample(input="This movie was great!")
    prompt = task.build_prompt(example)

    assert "positive" in prompt
    assert "negative" in prompt
    assert "neutral" in prompt
    assert "This movie was great!" in prompt
    assert "only the category name" in prompt


def test_classification_no_labels() -> None:
    task = ClassificationTask()
    example = EvalExample(input="test text")
    prompt = task.build_prompt(example)
    assert "test text" in prompt


def test_classification_run() -> None:
    task = ClassificationTask(labels=["A", "B"])
    model = FakeModel()
    example = EvalExample(input="test")
    result = task.run(example, model)

    assert result.output == "test output"
    assert result.latency_ms > 0
