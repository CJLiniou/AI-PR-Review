from typing import TYPE_CHECKING

from ..github.client import GitHubClient
from ..github.parser import parse_file_change, parse_github_pr_url
from .diff import build_diff_context
from .risk_rules import detect_rule_based_risks
from .summary import generate_rule_based_summary

if TYPE_CHECKING:
    from ..ai.risk_analyzer import AIRiskAnalyzer
    from ..ai.suggestion_generator import ReviewSuggestionGenerator
    from ..ai.summarizer import PRSummarizer


class ReviewService:
    def __init__(
        self,
        github_client: GitHubClient,
        summarizer: "PRSummarizer | None" = None,
        risk_analyzer: "AIRiskAnalyzer | None" = None,
        suggestion_generator: "ReviewSuggestionGenerator | None" = None,
    ) -> None:
        self._github = github_client
        self._summarizer = summarizer
        self._risk_analyzer = risk_analyzer
        self._suggestion_generator = suggestion_generator

    def review(self, pr_url: str) -> dict:
        parsed = parse_github_pr_url(pr_url)
        owner, repo, pull_number = parsed.owner, parsed.repo, parsed.pull_number

        pr = self._github.get_pull_request(owner, repo, pull_number)
        raw_files = self._github.get_pull_request_files(owner, repo, pull_number)
        commits = self._github.get_pull_request_commits(owner, repo, pull_number)

        file_changes = [
            parse_file_change(
                filename=f.filename,
                status=f.status,
                additions=f.additions,
                deletions=f.deletions,
                changes=f.changes,
                patch=f.patch,
            )
            for f in raw_files
        ]

        diff_context = build_diff_context(file_changes)
        summary = generate_rule_based_summary(file_changes)

        rule_risk_objs = detect_rule_based_risks(file_changes)
        rule_risks = [self._risk_to_dict(r) for r in rule_risk_objs]

        ai_risk_objs: list = []
        ai_risks: list[dict] = []
        if self._risk_analyzer is not None:
            ai_risk_objs = self._risk_analyzer.analyze(diff_context)
            ai_risks = [self._risk_to_dict(r) for r in ai_risk_objs]

        ai_summary = None
        if self._summarizer is not None:
            pr_info = {
                "title": pr.title,
                "author": pr.user.login,
                "description": pr.body or "",
                "files_changed": summary["total_files"],
                "additions": summary["total_additions"],
                "deletions": summary["total_deletions"],
                "commit_messages": [c.message for c in commits],
            }
            ai_summary = self._summarizer.summarize(pr_info, diff_context)

        review_suggestions = None
        if self._suggestion_generator is not None:
            all_risk_objs = rule_risk_objs + ai_risk_objs
            review_suggestions = self._suggestion_generator.generate(
                ai_summary or self._build_basic_summary(summary, pr),
                all_risk_objs,
            )

        return {
            "pr": {
                "title": pr.title,
                "author": pr.user.login,
                "state": pr.state,
                "base_branch": pr.base_branch,
                "head_branch": pr.head_branch,
                "head_sha": pr.head_sha,
                "html_url": pr.html_url,
            },
            "summary": summary,
            "ai_summary": ai_summary,
            "rule_risks": rule_risks,
            "ai_risks": ai_risks,
            "risks": rule_risks + ai_risks,
            "review_suggestions": review_suggestions,
            "commits": [{"sha": c.sha, "message": c.message, "author": c.author_name} for c in commits],
        }

    @staticmethod
    def _build_basic_summary(summary: dict, pr) -> str:
        return (
            f"PR: {pr.title}\n"
            f"文件变更数: {summary['total_files']}, "
            f"新增: {summary['total_additions']}, "
            f"删除: {summary['total_deletions']}"
        )

    def publish_review_comment(self, pr_url: str, review) -> str | None:
        parsed = parse_github_pr_url(pr_url)
        owner, repo, pull_number = parsed.owner, parsed.repo, parsed.pull_number

        markdown = getattr(review, "markdown_report", None) or ""
        if not markdown:
            return None

        result = self._github.create_issue_comment(owner, repo, pull_number, markdown)
        return result.get("html_url", "")

    @staticmethod
    def _risk_to_dict(r) -> dict:
        return {
            "file": r.file,
            "line": r.line,
            "risk_level": r.risk_level.value,
            "source": r.source.value,
            "category": r.category.value,
            "message": r.message,
            "suggestion": r.suggestion,
            "confidence": r.confidence.value,
        }
