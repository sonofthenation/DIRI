from pathlib import Path

from diri.core.models import DiriReport, ExpectedResultModel, Gap, MetricScore, TodoItem
from diri.evaluator.report_experience import evaluate_report_experience
from diri.report.console_report import render_console_report
from diri.scanner.project_scanner import scan_project


def test_report_experience_scores_existing_report_modules() -> None:
    project = scan_project(Path(__file__).resolve().parents[1])
    expected = ExpectedResultModel(result_summary="Build DIRI — Developer Intent Reproduction Index")

    score, evidence, missing = evaluate_report_experience(project, expected)

    assert score >= 70
    assert "diri/report/markdown_report.py" in evidence
    assert "diri/report/console_report.py" in evidence
    assert len(missing) < 4


def test_console_report_shows_next_actions() -> None:
    report = DiriReport(
        raw_score=60,
        trusted_score=45,
        confidence=75,
        level="Partial Reproduction",
        metric_scores={
            "intent_match": MetricScore(name="Intent Match", score=60, reasoning="Thin intent"),
        },
        gaps=[
            Gap(
                title="Functional gap",
                expected="capability",
                actual="missing",
                severity="high",
                affected_metric="functional_reproduction",
            )
        ],
        todo=[
            TodoItem(
                priority="high",
                title="Implement capability evidence",
                reason="Needed for functional reproduction",
                target_metric="functional_reproduction",
                expected_gain=12,
            )
        ],
    )

    output = render_console_report(report)

    assert "Next actions:" in output
    assert "[high] Implement capability evidence (+12)" in output
