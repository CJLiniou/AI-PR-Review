import argparse
import sys
from typing import Any

from .api.review import ReviewService


def _to_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return dict(value)


def format_markdown_report(review_result: Any) -> str:
    result = _to_dict(review_result)
    pr = result.get("pr") or {}
    summary = result.get("summary") or {}
    risks = result.get("risks") or []

    lines = [
        "# PR Review Report",
        "",
        "## PR",
    ]

    if pr:
        for key, value in pr.items():
            lines.append(f"- **{key}**: {value}")
    else:
        lines.append("- No PR metadata available.")

    lines.extend(["", "## Summary"])
    if summary:
        for key, value in summary.items():
            lines.append(f"- **{key}**: {value}")
    else:
        lines.append("- No summary available.")

    lines.extend(["", "## AI Summary", result.get("ai_summary") or "No AI summary available."])

    lines.extend(["", "## Risks"])
    if risks:
        for risk in risks:
            if isinstance(risk, dict):
                message = risk.get("message") or risk
                file = risk.get("file")
                prefix = f"{file}: " if file else ""
                lines.append(f"- {prefix}{message}")
            else:
                lines.append(f"- {risk}")
    else:
        lines.append("- No risks found.")

    lines.extend([
        "",
        "## Review Suggestions",
        result.get("review_suggestions") or "No review suggestions available.",
    ])

    return "\n".join(lines)


def run_review(pr_url: str) -> str:
    result = ReviewService().review(pr_url)
    return format_markdown_report(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-pr-review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser("review", help="Analyze a GitHub pull request.")
    review_parser.add_argument("pr_url", help="GitHub pull request URL.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review":
        report = run_review(args.pr_url)
        print(report)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
