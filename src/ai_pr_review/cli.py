import argparse
import sys

from .github.client import GitHubClient
from .report.markdown import MarkdownReportGenerator
from .review.service import ReviewService


def run_review(pr_url: str) -> str:
    result = ReviewService(GitHubClient()).review(pr_url)
    return MarkdownReportGenerator().generate(result)


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
