from typing import Any

from openai import AsyncOpenAI, OpenAI

from .base import Model


class OpenAIModel(Model):
    def __init__(
        self,
        model_id: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> None:
        self.model_id = model_id
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._temperature = temperature
        self._max_tokens = max_tokens

    def generate(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        messages = self._build_messages(prompt)
        params = {
            "model": self.model_id,
            "messages": messages,
            "temperature": kwargs.get("temperature", self._temperature),
            "max_tokens": kwargs.get("max_tokens", self._max_tokens),
        }
        response = self._client.chat.completions.create(**params)
        return response.choices[0].message.content or ""

    async def generate_async(self, prompt: str | list[dict[str, str]], **kwargs: Any) -> str:
        messages = self._build_messages(prompt)
        params = {
            "model": self.model_id,
            "messages": messages,
            "temperature": kwargs.get("temperature", self._temperature),
            "max_tokens": kwargs.get("max_tokens", self._max_tokens),
        }
        response = await self._async_client.chat.completions.create(**params)
        return response.choices[0].message.content or ""

    def _build_messages(self, prompt: str | list[dict[str, str]]) -> list[dict[str, str]]:
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        return prompt
