from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        raise NotImplementedError


class MockAIClient(AIClient):
    def chat(self, messages: list[dict]) -> str:
        return "mock response"
