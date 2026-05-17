from pathlib import Path

IMPORTANT_NAMES = {
    "README.md",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
}


def count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def summarize_file(path: Path, root: Path) -> str:
    relative = path.relative_to(root).as_posix()
    line_count = count_lines(path)
    if path.name in IMPORTANT_NAMES:
        return f"{relative}: important project file, {line_count} lines"
    return f"{relative}: {line_count} lines"


def build_tree_summary(files: list[Path], root: Path, max_items: int = 80) -> str:
    lines = []
    for file_path in files[:max_items]:
        lines.append(file_path.relative_to(root).as_posix())
    if len(files) > max_items:
        lines.append(f"... {len(files) - max_items} more files")
    return "\n".join(lines)
