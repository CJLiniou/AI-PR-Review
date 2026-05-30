import pytest

from ai_pr_review.ai.client import AIClient, MockAIClient


class TestAIClient:
    def test_cannot_instantiate_abstract(self):
        try:
            AIClient()  # type: ignore[abstract]
        except TypeError:
            pass
        else:
            pytest.fail("should have raised TypeError")

    def test_mock_client_returns_fixed_text(self):
        client = MockAIClient()
        result = client.chat([{"role": "user", "content": "hello"}])
        assert result == "mock response"

    def test_mock_client_is_aiclient(self):
        client = MockAIClient()
        assert isinstance(client, AIClient)

    def test_chat_accepts_multiple_messages(self):
        client = MockAIClient()
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Review this code."},
        ]
        result = client.chat(messages)
        assert result == "mock response"
