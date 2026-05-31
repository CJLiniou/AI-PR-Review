from abc import ABC, abstractmethod

from openai import OpenAI


class AIClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        raise NotImplementedError


class MockAIClient(AIClient):
    def chat(self, messages: list[dict]) -> str:
        return "mock response"


class OpenAIClient(AIClient):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def chat(self, messages: list[dict]) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
