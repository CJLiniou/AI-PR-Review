from ai_pr_review import cli


class FakeReviewService:
    called_with: str | None = None

    def review(self, pr_url: str) -> dict:
        self.__class__.called_with = pr_url
        return {
            "pr": {
                "url": pr_url,
                "number": 123,
                "title": "Test PR",
            },
            "summary": {
                "files_changed": 2,
                "additions": 10,
                "deletions": 3,
            },
            "ai_summary": "Mock AI summary.",
            "risks": [
                {
                    "file": "src/app.py",
                    "message": "Mock risk.",
                }
            ],
            "review_suggestions": "Mock suggestion.",
        }


def test_review_command_calls_review_service_and_outputs_markdown(monkeypatch, capsys):
    FakeReviewService.called_with = None
    monkeypatch.setattr("ai_pr_review.cli.ReviewService", FakeReviewService)

    exit_code = cli.main(["review", "https://github.com/owner/repo/pull/123"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert FakeReviewService.called_with == "https://github.com/owner/repo/pull/123"
    assert "# PR Review Report" in captured.out
    assert "## PR" in captured.out
    assert "- **number**: 123" in captured.out
    assert "## Summary" in captured.out
    assert "- **files_changed**: 2" in captured.out
    assert "## AI Summary" in captured.out
    assert "Mock AI summary." in captured.out
    assert "## Risks" in captured.out
    assert "- src/app.py: Mock risk." in captured.out
    assert "## Review Suggestions" in captured.out
    assert "Mock suggestion." in captured.out
