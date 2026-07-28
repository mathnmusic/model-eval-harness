from abc import ABC, abstractmethod


class Model(ABC):
    model_id: str

    @abstractmethod
    def generate(self, prompt: str | list[dict[str, str]], **kwargs) -> str:
        ...

    @abstractmethod
    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs) -> str:
        ...
