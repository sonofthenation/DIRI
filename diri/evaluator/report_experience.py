from dataclasses import dataclass, field
from pathlib import Path

from diri.core.models import ExpectedResultModel, ProjectSummary
from diri.evaluator.spec_capabilities import is_diri_spec


@dataclass(frozen=True)
class ReportExperienceCheck:
    name: str
    path: str
    required_terms: tuple[str, ...] = field(default_factory=tuple)


REPORT_EXPERIENCE_CHECKS = (
    ReportExperienceCheck("Console summary", "diri/report/console_report.py", ("Project DIRI Score", "Trusted DIRI Score", "Level")),
    ReportExperienceCheck("Console gap visibility", "diri/report/console_report.py", ("Main gaps", "affected_metric", "severity")),
    ReportExperienceCheck("Markdown summary", "diri/report/markdown_report.py", ("## Summary", "Raw DIRI Score", "DIRI Confidence")),
    ReportExperienceCheck("Markdown meaning", "diri/report/markdown_report.py", ("## Meaning",)),
    ReportExperienceCheck("Markdown metric table", "diri/report/markdown_report.py", ("## Metric Scores", "| Metric | Score | Meaning |")),
    ReportExperienceCheck("Markdown gap detail", "diri/report/markdown_report.py", ("## Main Gaps", "Expected:", "Actual:", "Severity:")),
    ReportExperienceCheck("Markdown TODO plan", "diri/report/markdown_report.py", ("## TODO Plan", "Expected gain", "Acceptance")),
    ReportExperienceCheck("Markdown recommendations", "diri/report/markdown_report.py", ("## Recommendations",)),
    ReportExperienceCheck("JSON report writer", "diri/report/json_report.py", ("write_json_report",)),
    ReportExperienceCheck("CLI plan output", "diri/cli.py", ("def plan", "expected_gain", "priority")),
)


def evaluate_report_experience(project: ProjectSummary, expected: ExpectedResultModel) -> tuple[int, list[str], list[str]]:
    if not is_diri_spec(expected):
        return 0, [], []

    root = Path(project.root)
    project_files = set(project.files)
    passed = 0
    evidence: list[str] = []
    missing: list[str] = []

    for check in REPORT_EXPERIENCE_CHECKS:
        if check.path not in project_files:
            missing.append(check.name)
            continue
        text = _read_text(root / check.path)
        if all(term.lower() in text.lower() for term in check.required_terms):
            passed += 1
            evidence.append(check.path)
        else:
            missing.append(check.name)

    score = round((passed / len(REPORT_EXPERIENCE_CHECKS)) * 100)
    return score, sorted(set(evidence)), missing


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
