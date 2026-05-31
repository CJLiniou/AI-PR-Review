from .models import Confidence, ReviewRisk

_CONFIDENCE_ORDER = {Confidence.LOW: 0, Confidence.MEDIUM: 1, Confidence.HIGH: 2}


def filter_risks_by_confidence(
    risks: list[ReviewRisk],
    min_confidence: str = "medium",
) -> list[ReviewRisk]:
    threshold = _CONFIDENCE_ORDER.get(Confidence(min_confidence), 1)
    return [r for r in risks if _CONFIDENCE_ORDER.get(r.confidence, 1) >= threshold]
