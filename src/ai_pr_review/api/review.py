import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..ai.client import MockAIClient, OpenAIClient
from ..ai.risk_analyzer import AIRiskAnalyzer
from ..ai.suggestion_generator import ReviewSuggestionGenerator
from ..ai.summarizer import PRSummarizer
from ..config import get_settings
from ..exceptions import (
    AIServiceError,
    GitHubAPIError,
    GitHubAuthError,
    InvalidPRUrlError,
    PullRequestNotFoundError,
)
from ..github.client import GitHubClient
from ..report.markdown import MarkdownReportGenerator
from ..review.service import ReviewService
from ..schemas import ApiResponse


class ReviewRequest(BaseModel):
    pr_url: str
    publish: bool = False


class ReviewResponse(BaseModel):
    pr: dict
    summary: dict
    ai_summary: str | None = None
    risks: list | None = None
    rule_risks: list | None = None
    ai_risks: list | None = None
    review_suggestions: str | None = None
    markdown_report: str | None = None
    comment_published: bool = False
    comment_url: str | None = None


router = APIRouter()


def get_review_service() -> ReviewService:
    settings = get_settings()

    ai_client = MockAIClient()
    if settings.llm_api_key:
        base_url = settings.llm_base_url or "https://api.openai.com/v1"
        ai_client = OpenAIClient(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=base_url,
            timeout=settings.request_timeout,
        )

    return ReviewService(
        github_client=GitHubClient(token=settings.github_token),
        summarizer=PRSummarizer(ai_client),
        risk_analyzer=AIRiskAnalyzer(ai_client),
        suggestion_generator=ReviewSuggestionGenerator(ai_client),
    )


@router.post("/review", response_model=ApiResponse[ReviewResponse])
def review_pull_request(
    request: ReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[ReviewResponse]:
    try:
        result = service.review(request.pr_url)
    except ValueError as exc:
        raise InvalidPRUrlError(str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 401 or status == 403:
            raise GitHubAuthError(f"GitHub 认证失败 (HTTP {status})，请检查 GITHUB_TOKEN") from exc
        if status == 404:
            raise PullRequestNotFoundError(f"PR 不存在或无权限访问 (HTTP {status})") from exc
        raise GitHubAPIError(f"GitHub API 错误 (HTTP {status}): {exc.response.text[:200]}") from exc

    if isinstance(result, dict):
        result["markdown_report"] = MarkdownReportGenerator().generate(result)
        result = ReviewResponse.model_validate(result)

    if not isinstance(result, ReviewResponse):
        result = ReviewResponse.model_validate(result)

    if request.publish and result.markdown_report:
        try:
            url = service.publish_review_comment(request.pr_url, result)
            result.comment_published = True
            result.comment_url = url
        except Exception:
            result.comment_published = False
            result.comment_url = None

    return ApiResponse(
        success=True,
        message="PR review completed.",
        data=result,
        error=None,
    )
