from ai_pr_review.github.models import FileChange, FileStatus
from ai_pr_review.review.models import ReviewRisk, RiskCategory, RiskLevel, RiskSource
from ai_pr_review.review.test_suggestions import generate_test_suggestions


class TestGenerateTestSuggestions:
    def test_empty_when_no_high_risk(self):
        files = [
            FileChange(
                filename="src/utils.py",
                status=FileStatus.MODIFIED,
                additions=5, deletions=1, changes=6, patch="dummy",
            )
        ]
        risks = [
            ReviewRisk(
                file="src/utils.py",
                risk_level=RiskLevel.LOW,
                source=RiskSource.RULE,
                category=RiskCategory.MAINTAINABILITY,
                message="minor",
                suggestion="fix",
            )
        ]
        assert generate_test_suggestions(files, risks) == []

    def test_reminds_when_high_risk_and_no_tests(self):
        files = [
            FileChange(
                filename="src/auth.py",
                status=FileStatus.MODIFIED,
                additions=10, deletions=2, changes=12, patch="dummy",
            )
        ]
        risks = [
            ReviewRisk(
                file="src/auth.py",
                risk_level=RiskLevel.HIGH,
                source=RiskSource.AI,
                category=RiskCategory.SECURITY,
                message="Hardcoded secret",
                suggestion="Use env var",
            )
        ]
        result = generate_test_suggestions(files, risks)
        assert len(result) >= 1
        assert any("未检测到测试文件" in s for s in result)

    def test_acknowledges_when_test_files_present(self):
        files = [
            FileChange(
                filename="src/auth.py",
                status=FileStatus.MODIFIED,
                additions=10, deletions=2, changes=12, patch="dummy",
            ),
            FileChange(
                filename="tests/test_auth.py",
                status=FileStatus.MODIFIED,
                additions=20, deletions=0, changes=20, patch="dummy",
            ),
        ]
        risks = [
            ReviewRisk(
                file="src/auth.py",
                risk_level=RiskLevel.HIGH,
                source=RiskSource.RULE,
                category=RiskCategory.SECURITY,
                message="auth changed",
                suggestion="review",
            )
        ]
        result = generate_test_suggestions(files, risks)
        assert any("已包含测试文件" in s for s in result)
