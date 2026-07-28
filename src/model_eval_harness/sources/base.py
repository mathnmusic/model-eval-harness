from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class EvalExample:
    input: str
    expected: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Source(ABC):
    @abstractmethod
    def load(self) -> Iterator[EvalExample]:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
