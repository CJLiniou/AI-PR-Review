from ai_pr_review import cli


class FakeReviewService:
    called_with: str | None = None

    def __init__(self, github_client=None) -> None:
        pass

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
    assert "# AI PR Review Report" in captured.out
    assert "## 1. PR 基本信息" in captured.out
    assert "Test PR" in captured.out
    assert "## 2. 变更统计" in captured.out
    assert "## 3. AI 总结" in captured.out
    assert "Mock AI summary." in captured.out
    assert "## 4. 风险项" in captured.out
    assert "Mock risk." in captured.out
    assert "## 5. Review 建议" in captured.out
    assert "Mock suggestion." in captured.out
