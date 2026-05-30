from ai_pr_review.review.models import (
    Confidence,
    ReviewRisk,
    RiskCategory,
    RiskLevel,
    RiskSource,
)


class TestReviewRisk:
    def test_create_minimal_risk(self):
        risk = ReviewRisk(
            file="src/auth.py",
            risk_level=RiskLevel.HIGH,
            source=RiskSource.RULE,
            category=RiskCategory.SECURITY,
            message="auth file modified",
            suggestion="review carefully",
        )
        assert risk.file == "src/auth.py"
        assert risk.risk_level == RiskLevel.HIGH
        assert risk.source == RiskSource.RULE
        assert risk.category == RiskCategory.SECURITY
        assert risk.line is None
        assert risk.confidence == Confidence.MEDIUM

    def test_create_full_risk(self):
        risk = ReviewRisk(
            file="src/payment.py",
            risk_level=RiskLevel.MEDIUM,
            source=RiskSource.AI,
            category=RiskCategory.LOGIC,
            message="Possible division by zero",
            suggestion="Add guard clause for zero denominator",
            line=42,
            confidence=Confidence.HIGH,
        )
        assert risk.line == 42
        assert risk.confidence == Confidence.HIGH
        assert risk.source == RiskSource.AI

    def test_risk_level_enum_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"

    def test_risk_source_enum_values(self):
        assert RiskSource.RULE.value == "rule"
        assert RiskSource.AI.value == "ai"

    def test_risk_category_enum_values(self):
        assert RiskCategory.SECURITY.value == "security"
        assert RiskCategory.PERFORMANCE.value == "performance"
        assert RiskCategory.LOGIC.value == "logic"
        assert RiskCategory.MAINTAINABILITY.value == "maintainability"
        assert RiskCategory.TESTING.value == "testing"
        assert RiskCategory.SCALE.value == "scale"

    def test_confidence_enum_values(self):
        assert Confidence.LOW.value == "low"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.HIGH.value == "high"

    def test_different_categories(self):
        cases = [
            (RiskCategory.SECURITY, "Secret key in logs"),
            (RiskCategory.PERFORMANCE, "N+1 query detected"),
            (RiskCategory.LOGIC, "Missing null check"),
            (RiskCategory.MAINTAINABILITY, "Function too long"),
            (RiskCategory.TESTING, "No test coverage"),
            (RiskCategory.SCALE, "PR too large"),
        ]
        for category, message in cases:
            risk = ReviewRisk(
                file="x.py",
                risk_level=RiskLevel.MEDIUM,
                source=RiskSource.RULE,
                category=category,
                message=message,
                suggestion="fix it",
            )
            assert risk.category == category
