from fnmatch import fnmatch
from pathlib import Path


def load_ignore_patterns(path: str = ".aiprignore") -> list[str]:
    ignore_file = Path(path)
    if not ignore_file.exists():
        return []

    patterns: list[str] = []
    for line in ignore_file.read_text(encoding="utf-8").splitlines():
        pattern = line.strip()
        if pattern and not pattern.startswith("#"):
            patterns.append(pattern)
    return patterns


def should_ignore_file(filename: str, patterns: list[str]) -> bool:
    normalized_filename = filename.replace("\\", "/").lstrip("./")
    basename = normalized_filename.rsplit("/", 1)[-1]

    for pattern in patterns:
        normalized_pattern = pattern.replace("\\", "/").strip().lstrip("./")
        if not normalized_pattern or normalized_pattern.startswith("#"):
            continue

        if normalized_pattern.endswith("/"):
            directory = normalized_pattern.rstrip("/")
            if normalized_filename == directory or normalized_filename.startswith(f"{directory}/"):
                return True
            continue

        if "/" in normalized_pattern:
            if fnmatch(normalized_filename, normalized_pattern):
                return True
            continue

        if fnmatch(basename, normalized_pattern) or fnmatch(normalized_filename, normalized_pattern):
            return True

    return False
