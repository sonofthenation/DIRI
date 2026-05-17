from pathlib import Path

from diri.constants import IGNORED_DIRS


def should_ignore(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if ".diri" in relative_parts and "reports" in relative_parts:
        return True
    return any(part in IGNORED_DIRS for part in relative_parts)


def collect_files(root: str | Path) -> list[Path]:
    root_path = Path(root).resolve()
    files: list[Path] = []
    for path in root_path.rglob("*"):
        if should_ignore(path, root_path):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)
