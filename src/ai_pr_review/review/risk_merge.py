from .models import Confidence, ReviewRisk


def merge_risks(
    rule_risks: list[ReviewRisk],
    ai_risks: list[ReviewRisk],
) -> list[ReviewRisk]:
    merged: dict[tuple[str, str | None, str, str], ReviewRisk] = {}

    for r in rule_risks + ai_risks:
        key = (r.file, r.line, r.category.value, r.message)
        existing = merged.get(key)
        if existing is None:
            merged[key] = r
            continue

        confidence_order = {Confidence.LOW: 0, Confidence.MEDIUM: 1, Confidence.HIGH: 2}
        if confidence_order.get(r.confidence, 1) > confidence_order.get(existing.confidence, 1):
            merged[key] = r
        elif (
            confidence_order.get(r.confidence, 1) == confidence_order.get(existing.confidence, 1)
            and r.source.value == "ai"
            and existing.source.value != "ai"
        ):
            merged[key] = r

    return list(merged.values())
