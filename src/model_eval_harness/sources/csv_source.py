import csv
from pathlib import Path
from typing import Any

from .base import EvalExample, Source


class CSVSource(Source):
    def __init__(
        self,
        path: str | Path,
        input_column: str,
        expected_column: str | None = None,
        limit: int | None = None,
    ) -> None:
        self._path = Path(path)
        self._input_column = input_column
        self._expected_column = expected_column
        self._limit = limit
        self._rows: list[dict[str, str]] = []

        with open(self._path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._rows.append(row)
                if limit and len(self._rows) >= limit:
                    break

    def load(self) -> Any:
        for row in self._rows:
            expected = None
            if self._expected_column and self._expected_column in row:
                expected = row[self._expected_column]
            yield EvalExample(
                input=row[self._input_column],
                expected=expected,
                metadata={"source": str(self._path)},
            )

    def __len__(self) -> int:
        return len(self._rows)
