from abc import ABC, abstractmethod
from typing import Any


class Model(ABC):
    model_id: str

    @abstractmethod
    def generate(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str: ...

    @abstractmethod
    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str: ...
