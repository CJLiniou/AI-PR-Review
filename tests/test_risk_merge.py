from ai_pr_review.review.models import (
    Confidence,
    ReviewRisk,
    RiskCategory,
    RiskLevel,
    RiskSource,
)
from ai_pr_review.review.risk_merge import merge_risks


class TestMergeRisks:
    def test_empty_lists(self):
        assert merge_risks([], []) == []

    def test_no_duplicates(self):
        rule = [
            ReviewRisk(
                file="a.py", risk_level=RiskLevel.HIGH, source=RiskSource.RULE,
                category=RiskCategory.SECURITY, message="risk A", suggestion="fix",
            )
        ]
        ai = [
            ReviewRisk(
                file="b.py", risk_level=RiskLevel.MEDIUM, source=RiskSource.AI,
                category=RiskCategory.LOGIC, message="risk B", suggestion="fix",
            )
        ]
        result = merge_risks(rule, ai)
        assert len(result) == 2

    def test_duplicate_prefers_higher_confidence(self):
        rule = [
            ReviewRisk(
                file="a.py", risk_level=RiskLevel.HIGH, source=RiskSource.RULE,
                category=RiskCategory.SECURITY, message="same", suggestion="rule",
                confidence=Confidence.MEDIUM,
            )
        ]
        ai = [
            ReviewRisk(
                file="a.py", risk_level=RiskLevel.HIGH, source=RiskSource.AI,
                category=RiskCategory.SECURITY, message="same", suggestion="ai",
                confidence=Confidence.HIGH,
            )
        ]
        result = merge_risks(rule, ai)
        assert len(result) == 1
        assert result[0].suggestion == "ai"

    def test_same_confidence_prefers_ai(self):
        rule = [
            ReviewRisk(
                file="a.py", risk_level=RiskLevel.HIGH, source=RiskSource.RULE,
                category=RiskCategory.SECURITY, message="same", suggestion="rule",
                confidence=Confidence.MEDIUM,
            )
        ]
        ai = [
            ReviewRisk(
                file="a.py", risk_level=RiskLevel.HIGH, source=RiskSource.AI,
                category=RiskCategory.SECURITY, message="same", suggestion="ai",
                confidence=Confidence.MEDIUM,
            )
        ]
        result = merge_risks(rule, ai)
        assert len(result) == 1
        assert result[0].source == RiskSource.AI
