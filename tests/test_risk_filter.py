from ai_pr_review.review.models import (
    Confidence,
    ReviewRisk,
    RiskCategory,
    RiskLevel,
    RiskSource,
)
from ai_pr_review.review.risk_filter import filter_risks_by_confidence


class TestFilterRisksByConfidence:
    def _make(self, level: str, confidence: str) -> ReviewRisk:
        return ReviewRisk(
            file="x.py",
            risk_level=RiskLevel(level),
            source=RiskSource.RULE,
            category=RiskCategory.LOGIC,
            message=level,
            suggestion="fix",
            confidence=Confidence(confidence),
        )

    def test_empty(self):
        assert filter_risks_by_confidence([]) == []

    def test_default_medium_filters_low(self):
        risks = [
            self._make("high", "high"),
            self._make("medium", "medium"),
            self._make("low", "low"),
        ]
        result = filter_risks_by_confidence(risks)
        assert len(result) == 2
        levels = {r.risk_level.value for r in result}
        assert "low" not in levels

    def test_min_high_only_keeps_high(self):
        risks = [
            self._make("high", "high"),
            self._make("medium", "medium"),
        ]
        result = filter_risks_by_confidence(risks, min_confidence="high")
        assert len(result) == 1
        assert result[0].risk_level == RiskLevel.HIGH

    def test_min_low_keeps_all(self):
        risks = [
            self._make("low", "low"),
            self._make("high", "high"),
        ]
        result = filter_risks_by_confidence(risks, min_confidence="low")
        assert len(result) == 2
