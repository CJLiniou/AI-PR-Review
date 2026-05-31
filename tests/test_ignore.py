from ai_pr_review.review.ignore import load_ignore_patterns, should_ignore_file


def test_load_ignore_patterns_reads_non_empty_non_comment_lines(tmp_path):
    ignore_file = tmp_path / ".aiprignore"
    ignore_file.write_text(
        "# comment\n\n"
        "dist/\n"
        "generated/\n"
        "*.min.js\n"
        "package-lock.json\n",
        encoding="utf-8",
    )

    patterns = load_ignore_patterns(str(ignore_file))

    assert patterns == ["dist/", "generated/", "*.min.js", "package-lock.json"]


def test_load_ignore_patterns_returns_empty_list_for_missing_file(tmp_path):
    patterns = load_ignore_patterns(str(tmp_path / ".aiprignore"))

    assert patterns == []


def test_should_ignore_directory_patterns():
    patterns = ["dist/", "generated/"]

    assert should_ignore_file("dist/app.js", patterns) is True
    assert should_ignore_file("generated/client.py", patterns) is True
    assert should_ignore_file("src/app.py", patterns) is False


def test_should_ignore_wildcard_patterns():
    patterns = ["*.min.js"]

    assert should_ignore_file("assets/app.min.js", patterns) is True
    assert should_ignore_file("assets/app.js", patterns) is False


def test_should_ignore_exact_filename_patterns():
    patterns = ["package-lock.json"]

    assert should_ignore_file("package-lock.json", patterns) is True
    assert should_ignore_file("frontend/package-lock.json", patterns) is True
    assert should_ignore_file("package.json", patterns) is False
