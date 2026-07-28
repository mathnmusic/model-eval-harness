import time
from typing import Any

from ..sources.base import EvalExample
from .base import Task, TaskResult


class TextGenerationTask(Task):
    def __init__(self, instruction: str = "") -> None:
        self._instruction = instruction

    def build_prompt(self, example: EvalExample) -> str:
        if self._instruction:
            return f"{self._instruction}\n\n{example.input}"
        return example.input

    def post_process(self, output: str, example: EvalExample) -> str:
        return output.strip()

    def run(self, example: EvalExample, model: Any) -> TaskResult:
        prompt = self.build_prompt(example)
        start = time.perf_counter()
        output = model.generate(prompt)
        latency = (time.perf_counter() - start) * 1000
        processed = self.post_process(output, example)
        return TaskResult(
            example=example,
            output=processed,
            raw_response=output,
            latency_ms=latency,
        )


class ClassificationTask(Task):
    def __init__(
        self,
        labels: list[str] | None = None,
        instruction: str = "Classify the following text into one of these categories:",
    ) -> None:
        self._labels = labels
        self._instruction = instruction

    def build_prompt(self, example: EvalExample) -> str:
        parts = [self._instruction]
        if self._labels:
            parts.append(f"Categories: {', '.join(self._labels)}")
        parts.append(f"\nText: {example.input}")
        parts.append("\nAnswer with only the category name.")
        return "\n".join(parts)

    def post_process(self, output: str, example: EvalExample) -> str:
        return output.strip()

    def run(self, example: EvalExample, model: Any) -> TaskResult:
        prompt = self.build_prompt(example)
        start = time.perf_counter()
        output = model.generate(prompt)
        latency = (time.perf_counter() - start) * 1000
        processed = self.post_process(output, example)
        return TaskResult(
            example=example,
            output=processed,
            raw_response=output,
            latency_ms=latency,
        )
