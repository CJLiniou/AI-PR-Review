from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskSource(str, Enum):
    RULE = "rule"
    AI = "ai"


class RiskCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    SCALE = "scale"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ReviewRisk:
    file: str
    risk_level: RiskLevel
    source: RiskSource
    category: RiskCategory
    message: str
    suggestion: str
    line: int | None = None
    confidence: Confidence = Confidence.MEDIUM
