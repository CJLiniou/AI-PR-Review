from ai_pr_review.report.markdown import MarkdownReportGenerator


def _make_basic_result() -> dict:
    return {
        "pr": {
            "title": "Fix auth bug",
            "author": "alice",
            "state": "open",
            "head_branch": "feature/fix-auth",
            "base_branch": "main",
            "head_sha": "abc1234",
        },
        "summary": {
            "total_files": 3,
            "total_additions": 42,
            "total_deletions": 10,
            "total_changes": 52,
            "top_directories": [
                {"directory": "src", "files": 2},
                {"directory": "tests", "files": 1},
            ],
            "file_extensions": [
                {"extension": ".py", "count": 3},
            ],
        },
        "ai_summary": None,
        "risks": [
            {
                "file": "src/auth.py",
                "line": 42,
                "risk_level": "high",
                "source": "ai",
                "category": "security",
                "message": "Hardcoded secret key",
                "suggestion": "Use env variable instead",
            },
            {
                "file": "src/utils.py",
                "line": None,
                "risk_level": "medium",
                "source": "rule",
                "category": "maintainability",
                "message": "Function is too long",
                "suggestion": "Refactor into smaller functions",
            },
        ],
        "review_suggestions": None,
    }


class TestMarkdownReportGenerator:
    def test_generates_all_sections(self):
        gen = MarkdownReportGenerator()
        report = gen.generate(_make_basic_result())

        assert "# AI PR Review Report" in report
        assert "## 1. PR 基本信息" in report
        assert "## 2. 变更统计" in report
        assert "## 3. AI 总结" in report
        assert "## 4. 风险项" in report
        assert "## 5. Review 建议" in report
        assert "## 6. 测试建议" in report

    def test_shows_placeholder_when_no_ai_summary(self):
        gen = MarkdownReportGenerator()
        report = gen.generate(_make_basic_result())
        assert "暂无" in report

    def test_shows_ai_summary_when_present(self):
        result = _make_basic_result()
        result["ai_summary"] = "This PR fixes a critical auth bug"
        gen = MarkdownReportGenerator()
        report = gen.generate(result)
        assert "This PR fixes a critical auth bug" in report
        assert "AI 总结" in report

    def test_shows_review_suggestions_when_present(self):
        result = _make_basic_result()
        result["review_suggestions"] = "Focus on auth module"
        gen = MarkdownReportGenerator()
        report = gen.generate(result)
        assert "Focus on auth module" in report

    def test_risk_summary_counts(self):
        result = _make_basic_result()
        result["risks"].append({
            "file": "x.py",
            "risk_level": "low",
            "source": "rule",
            "category": "logic",
            "message": "Minor",
            "suggestion": "",
        })
        gen = MarkdownReportGenerator()
        report = gen.generate(result)
        assert "高危: 1" in report
        assert "中危: 1" in report
        assert "低危: 1" in report

    def test_empty_risks(self):
        result = _make_basic_result()
        result["risks"] = []
        gen = MarkdownReportGenerator()
        report = gen.generate(result)
        assert "暂无" in report

    def test_empty_summary(self):
        result = {
            "pr": {"title": "Test"},
            "summary": {},
            "ai_summary": None,
            "risks": [],
            "review_suggestions": None,
        }
        gen = MarkdownReportGenerator()
        report = gen.generate(result)
        assert isinstance(report, str)
        assert "## 1. PR 基本信息" in report
