from pathlib import Path

from diri.core.models import ExpectedResultModel
from diri.evaluator.intent_alignment import evaluate_intent_alignment
from diri.scanner.project_scanner import scan_project


def test_intent_alignment_scores_diri_philosophy_evidence() -> None:
    project = scan_project(Path(__file__).resolve().parents[1])
    expected = ExpectedResultModel(result_summary="Build DIRI — Developer Intent Reproduction Index")

    score, evidence, missing = evaluate_intent_alignment(project, expected)

    assert score >= 70
    assert "README.md" in evidence
    assert "diri/core/models.py" in evidence
    assert len(missing) < 3
