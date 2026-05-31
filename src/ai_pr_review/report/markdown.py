class MarkdownReportGenerator:
    def generate(self, review_result: dict) -> str:
        sections: list[str] = []
        sections.append(self._render_header(review_result))
        sections.append(self._render_pr_summary(review_result))
        sections.append(self._render_change_stats(review_result))
        sections.append(self._render_ai_summary(review_result))
        sections.append(self._render_risks(review_result))
        sections.append(self._render_suggestions(review_result))
        sections.append(self._render_test_suggestions(review_result))
        return "\n\n".join(sections)

    @staticmethod
    def _render_header(review_result: dict) -> str:
        pr = review_result.get("pr", {})
        title = pr.get("title", "Unknown")
        return f"# AI PR Review Report\n\n**PR**: {title}\n\n**Author**: {pr.get('author', 'N/A')}  \n**Branch**: {pr.get('head_branch', 'N/A')} → {pr.get('base_branch', 'N/A')}  \n**State**: {pr.get('state', 'N/A')}"

    @staticmethod
    def _render_pr_summary(review_result: dict) -> str:
        pr = review_result.get("pr", {})
        return (
            "## 1. PR 基本信息\n\n"
            f"- **标题**: {pr.get('title', 'N/A')}\n"
            f"- **作者**: {pr.get('author', 'N/A')}\n"
            f"- **分支**: {pr.get('head_branch', 'N/A')} → {pr.get('base_branch', 'N/A')}\n"
            f"- **状态**: {pr.get('state', 'N/A')}\n"
            f"- **HEAD SHA**: `{pr.get('head_sha', 'N/A')}`"
        )

    @staticmethod
    def _render_change_stats(review_result: dict) -> str:
        s = review_result.get("summary", {})
        if not s:
            return "## 2. 变更统计\n\n暂无"

        lines = [
            "## 2. 变更统计",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 变更文件数 | {s.get('total_files', 0)} |",
            f"| 新增行数 | {s.get('total_additions', 0)} |",
            f"| 删除行数 | {s.get('total_deletions', 0)} |",
            f"| 总变更行数 | {s.get('total_changes', 0)} |",
        ]

        dirs = s.get("top_directories", [])
        if dirs:
            lines.append("")
            lines.append("### 主要变更目录")
            lines.append("")
            for d in dirs[:5]:
                lines.append(f"- `{d['directory']}/` — {d['files']} 个文件")

        exts = s.get("file_extensions", [])
        if exts:
            lines.append("")
            lines.append("### 文件类型分布")
            lines.append("")
            for e in exts[:5]:
                lines.append(f"- `{e['extension']}` — {e['count']} 个文件")

        return "\n".join(lines)

    @staticmethod
    def _render_ai_summary(review_result: dict) -> str:
        ai_summary = review_result.get("ai_summary")
        if not ai_summary:
            return "## 3. AI 总结\n\n暂无"
        return f"## 3. AI 总结\n\n{ai_summary}"

    @staticmethod
    def _render_risks(review_result: dict) -> str:
        risks = review_result.get("risks", [])
        if not risks:
            return "## 4. 风险项\n\n暂无"

        lines = ["## 4. 风险项", ""]
        high = [r for r in risks if r.get("risk_level") == "high"]
        medium = [r for r in risks if r.get("risk_level") == "medium"]
        low = [r for r in risks if r.get("risk_level") == "low"]

        lines.append(f"共识别 {len(risks)} 个风险项（高危: {len(high)}, 中危: {len(medium)}, 低危: {len(low)}）")
        lines.append("")

        for r in risks:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r.get("risk_level", ""), "⚪")
            source = r.get("source", "")
            source_label = "规则" if source == "rule" else "AI" if source == "ai" else source
            file = r.get("file", "")
            line = f":{r['line']}" if r.get("line") else ""
            lines.append(f"- {emoji} **[{r.get('risk_level', '').upper()}]** [{r.get('category', '')}] `{file}{line}` ({source_label})")
            lines.append(f"  > {r.get('message', '')}")
            suggestion = r.get("suggestion", "")
            if suggestion:
                lines.append(f"  > 建议: {suggestion}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _render_suggestions(review_result: dict) -> str:
        suggestions = review_result.get("review_suggestions")
        if not suggestions:
            return "## 5. Review 建议\n\n暂无"
        return f"## 5. Review 建议\n\n{suggestions}"

    @staticmethod
    def _render_test_suggestions(review_result: dict) -> str:
        return "## 6. 测试建议\n\n暂无"
