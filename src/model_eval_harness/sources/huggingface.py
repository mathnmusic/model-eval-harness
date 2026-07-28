from typing import Any

from datasets import load_dataset

from .base import EvalExample, Source


class HuggingFaceSource(Source):
    def __init__(
        self,
        dataset_name: str,
        split: str = "test",
        input_column: str = "question",
        expected_column: str | None = "answer",
        config: str | None = None,
        limit: int | None = None,
    ) -> None:
        self._dataset_name = dataset_name
        self._split = split
        self._input_column = input_column
        self._expected_column = expected_column
        self._config = config
        self._limit = limit

        load_kwargs: dict[str, Any] = {"path": dataset_name, "split": split}
        if config:
            load_kwargs["name"] = config
        self._data = list(load_dataset(**load_kwargs))

        if limit:
            self._data = self._data[:limit]

    def load(self) -> Any:
        for row in self._data:
            expected = None
            if self._expected_column and self._expected_column in row:
                expected = str(row[self._expected_column])
            yield EvalExample(
                input=str(row[self._input_column]),
                expected=expected,
                metadata={"source": self._dataset_name, "split": self._split},
            )

    def __len__(self) -> int:
        return len(self._data)
