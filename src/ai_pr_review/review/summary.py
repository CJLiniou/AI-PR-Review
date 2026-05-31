from collections import Counter
from pathlib import PurePosixPath

from ..github.models import FileChange


def generate_rule_based_summary(files: list[FileChange]) -> dict:
    total_files = len(files)
    total_additions = sum(f.additions for f in files)
    total_deletions = sum(f.deletions for f in files)
    total_changes = sum(f.changes for f in files)

    dir_counter: Counter[str] = Counter()
    ext_counter: Counter[str] = Counter()

    for f in files:
        path = PurePosixPath(f.filename)
        parts = path.parts
        if len(parts) > 1:
            dir_counter[parts[0]] += 1
        else:
            dir_counter["(root)"] += 1

        suffix = path.suffix.lower() or "(no extension)"
        ext_counter[suffix] += 1

    return {
        "total_files": total_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "total_changes": total_changes,
        "top_directories": [
            {"directory": d, "files": c}
            for d, c in dir_counter.most_common()
        ],
        "file_extensions": [
            {"extension": e, "count": c}
            for e, c in ext_counter.most_common()
        ],
    }
