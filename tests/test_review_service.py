from unittest.mock import MagicMock

from ai_pr_review.ai.risk_analyzer import AIRiskAnalyzer
from ai_pr_review.ai.suggestion_generator import ReviewSuggestionGenerator
from ai_pr_review.ai.summarizer import PRSummarizer
from ai_pr_review.github.client import GitHubClient
from ai_pr_review.github.models import (
    GitHubChangedFile,
    GitHubCommit,
    GitHubPullRequest,
    GitHubUser,
)
from ai_pr_review.review.service import ReviewService


def _mock_pr() -> GitHubPullRequest:
    return GitHubPullRequest(
        number=1,
        title="Test PR",
        body="A test PR description",
        state="open",
        html_url="https://github.com/owner/repo/pull/1",
        user=GitHubUser(login="dev", html_url="https://github.com/dev"),
        base_branch="main",
        head_branch="feature",
        head_sha="abc123",
        created_at="2026-01-01",
        updated_at="2026-01-01",
    )


def _mock_files() -> list[GitHubChangedFile]:
    return [
        GitHubChangedFile(
            filename="src/auth.py",
            status="modified",
            additions=10,
            deletions=2,
            changes=12,
            patch="@@ -1,3 +1,5 @@\n def login():\n+    return True",
            raw_url="",
            blob_url="",
        ),
        GitHubChangedFile(
            filename="README.md",
            status="modified",
            additions=1,
            deletions=1,
            changes=2,
            patch="@@ -1,1 +1,1 @@\n-old\n+new",
            raw_url="",
            blob_url="",
        ),
    ]


def _mock_commits() -> list[GitHubCommit]:
    return [
        GitHubCommit(
            sha="abc123",
            message="fix: auth bug",
            author_name="alice",
            author_email="a@test.com",
        ),
        GitHubCommit(
            sha="def456",
            message="test: add auth tests",
            author_name="alice",
            author_email="a@test.com",
        ),
    ]


class TestReviewService:
    def test_review_returns_structured_result(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        service = ReviewService(client)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert "pr" in result
        assert result["pr"]["title"] == "Test PR"
        assert result["pr"]["author"] == "dev"

        assert "summary" in result
        assert result["summary"]["total_files"] == 2
        assert result["summary"]["total_additions"] == 11

        assert "risks" in result
        assert "rule_risks" in result
        assert "ai_risks" in result
        assert len(result["risks"]) >= 1
        assert len(result["rule_risks"]) >= 1
        assert result["ai_risks"] == []
        risk = result["risks"][0]
        assert "file" in risk
        assert "risk_level" in risk
        assert "category" in risk
        assert "message" in risk

        assert "ai_summary" in result
        assert result["ai_summary"] is None
        assert "review_suggestions" in result
        assert result["review_suggestions"] is None

    def test_review_calls_github_client_correctly(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        service = ReviewService(client)
        service.review("https://github.com/owner/repo/pull/42")

        client.get_pull_request.assert_called_once_with("owner", "repo", 42)
        client.get_pull_request_files.assert_called_once_with("owner", "repo", 42)

    def test_no_risk_files_returns_empty_risks(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = [
            GitHubChangedFile(
                filename="src/utils.py",
                status="modified",
                additions=3,
                deletions=1,
                changes=4,
                patch="@@ -1,1 +1,1 @@\n-old\n+new",
            raw_url="",
            blob_url="",
            )
        ]

        service = ReviewService(client)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["risks"] == []
        assert result["summary"]["total_files"] == 1

    def test_ai_summary_populated_when_summarizer_provided(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        summarizer = MagicMock(spec=PRSummarizer)
        summarizer.summarize.return_value = "AI generated PR summary"

        service = ReviewService(client, summarizer=summarizer)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["ai_summary"] == "AI generated PR summary"
        summarizer.summarize.assert_called_once()

    def test_ai_summary_none_when_no_summarizer(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        service = ReviewService(client)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["ai_summary"] is None

    def test_ai_risks_populated_when_analyzer_provided(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        analyzer = MagicMock(spec=AIRiskAnalyzer)
        from ai_pr_review.review.models import (
            Confidence,
            ReviewRisk,
            RiskCategory,
            RiskLevel,
            RiskSource,
        )
        analyzer.analyze.return_value = [
            ReviewRisk(
                file="src/auth.py",
                risk_level=RiskLevel.HIGH,
                source=RiskSource.AI,
                category=RiskCategory.SECURITY,
                message="AI detected risk",
                suggestion="Fix it",
            )
        ]

        service = ReviewService(client, risk_analyzer=analyzer)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert len(result["ai_risks"]) == 1
        assert result["ai_risks"][0]["message"] == "AI detected risk"
        assert result["ai_risks"][0]["source"] == "ai"
        assert len(result["rule_risks"]) >= 1
        assert len(result["risks"]) == len(result["rule_risks"]) + len(result["ai_risks"])

    def test_ai_risks_empty_when_no_analyzer(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        service = ReviewService(client)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["ai_risks"] == []
        assert result["risks"] == result["rule_risks"]

    def test_suggestions_populated_when_generator_provided(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        gen = MagicMock(spec=ReviewSuggestionGenerator)
        gen.generate.return_value = "Please review auth module carefully"

        service = ReviewService(client, suggestion_generator=gen)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["review_suggestions"] == "Please review auth module carefully"
        gen.generate.assert_called_once()

    def test_suggestions_none_when_no_generator(self):
        client = MagicMock(spec=GitHubClient)
        client.get_pull_request.return_value = _mock_pr()
        client.get_pull_request_files.return_value = _mock_files()
        client.get_pull_request_commits.return_value = _mock_commits()

        service = ReviewService(client)
        result = service.review("https://github.com/owner/repo/pull/1")

        assert result["review_suggestions"] is None
