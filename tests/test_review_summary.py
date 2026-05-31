from ai_pr_review.github.models import FileChange, FileStatus
from ai_pr_review.review.summary import generate_rule_based_summary


class TestGenerateRuleBasedSummary:
    def test_empty_files(self):
        result = generate_rule_based_summary([])
        assert result["total_files"] == 0
        assert result["total_additions"] == 0
        assert result["total_deletions"] == 0
        assert result["total_changes"] == 0
        assert result["top_directories"] == []
        assert result["file_extensions"] == []

    def test_single_python_file(self):
        files = [
            FileChange(
                filename="src/auth.py",
                status=FileStatus.MODIFIED,
                additions=10,
                deletions=2,
                changes=12,
                patch="dummy",
            )
        ]
        result = generate_rule_based_summary(files)
        assert result["total_files"] == 1
        assert result["total_additions"] == 10
        assert result["total_deletions"] == 2
        assert result["total_changes"] == 12
        assert result["top_directories"][0]["directory"] == "src"
        assert result["top_directories"][0]["files"] == 1
        assert result["file_extensions"][0]["extension"] == ".py"
        assert result["file_extensions"][0]["count"] == 1

    def test_multiple_files_multiple_dirs(self):
        files = [
            FileChange(
                filename="src/api/health.py",
                status=FileStatus.MODIFIED,
                additions=5,
                deletions=1,
                changes=6,
                patch="dummy",
            ),
            FileChange(
                filename="src/api/review.py",
                status=FileStatus.ADDED,
                additions=20,
                deletions=0,
                changes=20,
                patch="dummy",
            ),
            FileChange(
                filename="tests/test_health.py",
                status=FileStatus.ADDED,
                additions=15,
                deletions=0,
                changes=15,
                patch="dummy",
            ),
            FileChange(
                filename="README.md",
                status=FileStatus.MODIFIED,
                additions=3,
                deletions=1,
                changes=4,
                patch="dummy",
            ),
        ]
        result = generate_rule_based_summary(files)
        assert result["total_files"] == 4
        assert result["total_additions"] == 43
        assert result["total_deletions"] == 2
        assert result["total_changes"] == 45

        dir_names = [d["directory"] for d in result["top_directories"]]
        assert "src" in dir_names
        assert "tests" in dir_names
        assert "(root)" in dir_names

        exts = {e["extension"]: e["count"] for e in result["file_extensions"]}
        assert exts[".py"] == 3
        assert exts[".md"] == 1

    def test_root_level_file(self):
        files = [
            FileChange(
                filename="main.py",
                status=FileStatus.MODIFIED,
                additions=1,
                deletions=1,
                changes=2,
                patch="dummy",
            )
        ]
        result = generate_rule_based_summary(files)
        assert result["top_directories"][0]["directory"] == "(root)"

    def test_file_without_extension(self):
        files = [
            FileChange(
                filename="Dockerfile",
                status=FileStatus.ADDED,
                additions=5,
                deletions=0,
                changes=5,
                patch="dummy",
            )
        ]
        result = generate_rule_based_summary(files)
        assert result["file_extensions"][0]["extension"] == "(no extension)"

    def test_directories_sorted_by_count(self):
        files = [
            FileChange(
                filename="src/a.py", status=FileStatus.MODIFIED,
                additions=1, deletions=0, changes=1, patch="dummy",
            ),
            FileChange(
                filename="src/b.py", status=FileStatus.MODIFIED,
                additions=1, deletions=0, changes=1, patch="dummy",
            ),
            FileChange(
                filename="src/sub/c.py", status=FileStatus.MODIFIED,
                additions=1, deletions=0, changes=1, patch="dummy",
            ),
            FileChange(
                filename="tests/test_x.py", status=FileStatus.ADDED,
                additions=1, deletions=0, changes=1, patch="dummy",
            ),
        ]
        result = generate_rule_based_summary(files)
        top = result["top_directories"]
        assert top[0]["directory"] == "src"
        assert top[0]["files"] == 3
        assert top[1]["directory"] == "tests"
        assert top[1]["files"] == 1
