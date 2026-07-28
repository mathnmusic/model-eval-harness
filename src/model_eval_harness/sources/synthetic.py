from typing import Any

from .base import EvalExample, Source


class SyntheticSource(Source):
    def __init__(
        self,
        spec: str,
        count: int = 10,
        model: Any = None,
        seed_examples: list[EvalExample] | None = None,
    ) -> None:
        self._spec = spec
        self._count = count
        self._model = model
        self._examples: list[EvalExample] = list(seed_examples or [])
        self._generated = False

    def _generate(self) -> None:
        if self._generated:
            return
        needed = self._count - len(self._examples)
        if not self._model:
            for _ in range(needed):
                self._examples.append(
                    EvalExample(
                        input=f"[synthetic:{self._spec}] Example {len(self._examples) + 1}",
                        expected=None,
                        metadata={"source": "synthetic", "index": len(self._examples)},
                    )
                )
        else:
            for _ in range(needed):
                example = self._generate_one()
                if example:
                    self._examples.append(example)
        self._generated = True

    def _generate_one(self) -> EvalExample | None:
        prompt = (
            f"Generate one test example for this evaluation spec: {self._spec}\n"
            'Respond in JSON format: {"input": "...", "expected": "..."}\n'
            "Only output valid JSON, no other text."
        )
        try:
            output = self._model.generate(prompt)
            import json

            data = json.loads(output.strip().removeprefix("```json").removesuffix("```").strip())
            return EvalExample(
                input=data["input"],
                expected=data.get("expected"),
                metadata={"source": "synthetic"},
            )
        except Exception:
            return None

    def load(self) -> Any:
        self._generate()
        yield from self._examples

    def __len__(self) -> int:
        self._generate()
        return len(self._examples)
