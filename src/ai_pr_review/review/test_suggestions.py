from ..github.models import FileChange
from ..review.models import ReviewRisk, RiskLevel
from .file_classifier import is_test_file


def generate_test_suggestions(
    files: list[FileChange],
    risks: list[ReviewRisk],
) -> list[str]:
    suggestions: list[str] = []

    has_high_risk = any(r.risk_level == RiskLevel.HIGH for r in risks)
    if not has_high_risk:
        return suggestions

    has_test_changes = any(is_test_file(f.filename) for f in files)
    if has_test_changes:
        suggestions.append("已包含测试文件变更，请确认测试覆盖了所有高风险变更路径")
        return suggestions

    suggestions.append(
        "此 PR 包含高风险变更，但未检测到测试文件变更"
        "，建议补充以下测试："
    )

    non_test_files = [f for f in files if not is_test_file(f.filename)]
    security_files = [
        f.filename for f in non_test_files
        if any(kw in f.filename.lower() for kw in ("auth", "security", "permission", "role"))
    ]
    if security_files:
        suggestions.append(f"- 安全相关文件变更需补充安全测试: {', '.join(security_files[:3])}")

    payment_files = [
        f.filename for f in non_test_files
        if any(kw in f.filename.lower() for kw in ("payment", "billing"))
    ]
    if payment_files:
        suggestions.append(f"- 支付相关文件变更需补充事务和边界测试: {', '.join(payment_files[:3])}")

    migration_files = [
        f.filename for f in non_test_files
        if any(kw in f.filename.lower() for kw in ("migration", "migrate"))
    ]
    if migration_files:
        suggestions.append(f"- 迁移文件变更建议补充回滚测试: {', '.join(migration_files[:3])}")

    if not security_files and not payment_files and not migration_files:
        suggestions.append(
            f"- 建议为以下高风险文件补充测试: "
            f"{', '.join(f.filename for f in non_test_files[:3])}"
        )

    return suggestions
