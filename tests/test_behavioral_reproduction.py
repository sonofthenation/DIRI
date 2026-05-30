from pathlib import Path

from diri.core.models import DeveloperIntent, ExpectedResultModel, ProjectSummary
from diri.evaluator.metric_evaluator import evaluate_metrics
from diri.scanner.file_collector import should_ignore

BASE_FILES = [
    "diri/cli.py",
    ".diri/intent.json",
    ".diri/expected_result.json",
    "tests/test_x.py",
]


def _project(root: Path) -> ProjectSummary:
    return ProjectSummary(root=str(root), files=list(BASE_FILES), languages={"Python": 1})


def test_scanner_still_hides_report_artifacts(tmp_path: Path) -> None:
    report = tmp_path / ".diri" / "reports" / "latest.json"
    assert should_ignore(report, tmp_path) is True


def test_persisted_reports_lift_behavioral_reproduction(tmp_path: Path) -> None:
    reports = tmp_path / ".diri" / "reports"
    reports.mkdir(parents=True)
    (reports / "latest.json").write_text("{}", encoding="utf-8")

    metrics = evaluate_metrics(DeveloperIntent(), ExpectedResultModel(), _project(tmp_path))
    assert metrics["behavioral_reproduction"].score >= 95


def test_no_reports_keeps_behavioral_reproduction_lower(tmp_path: Path) -> None:
    metrics = evaluate_metrics(DeveloperIntent(), ExpectedResultModel(), _project(tmp_path))
    assert metrics["behavioral_reproduction"].score == 85
