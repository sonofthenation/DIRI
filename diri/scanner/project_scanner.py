from pathlib import Path

from diri.core.models import ProjectSummary
from diri.scanner.code_summarizer import build_tree_summary, count_lines, summarize_file
from diri.scanner.file_collector import collect_files
from diri.scanner.language_detector import detect_language


def scan_project(project_path: str | Path) -> ProjectSummary:
    root = Path(project_path).resolve()
    files = collect_files(root)
    languages: dict[str, int] = {}
    important_files: list[str] = []
    file_summaries: dict[str, str] = {}
    total_lines = 0

    for file_path in files:
        relative = file_path.relative_to(root).as_posix()
        language = detect_language(file_path.name)
        languages[language] = languages.get(language, 0) + 1
        lines = count_lines(file_path)
        total_lines += lines
        file_summaries[relative] = summarize_file(file_path, root)
        if file_path.name in {"README.md", "pyproject.toml", "package.json", "requirements.txt"} or relative.startswith("diri/"):
            important_files.append(relative)

    return ProjectSummary(
        root=str(root),
        files=[file_path.relative_to(root).as_posix() for file_path in files],
        languages=languages,
        important_files=important_files,
        total_files=len(files),
        total_lines=total_lines,
        tree_summary=build_tree_summary(files, root),
        file_summaries=file_summaries,
    )
