from pathlib import Path

from diri.core.models import ExpectedResultModel, ProjectSummary
from diri.evaluator.spec_capabilities import evaluate_diri_capabilities, is_diri_spec


def test_detects_diri_spec_from_expected_result() -> None:
    expected = ExpectedResultModel(result_summary="Build DIRI — Developer Intent Reproduction Index")

    assert is_diri_spec(expected)


def test_diri_capability_score_uses_concrete_evidence(tmp_path: Path) -> None:
    files = {
        "pyproject.toml": "typer\npydantic\n",
        "diri/cli.py": "init discover score plan self-score compare\n",
        "diri/core/models.py": "DeveloperIntent ExpectedResultModel DiriReport\n",
        "diri/core/scoring.py": "calculate_raw_score calculate_trusted_score\n",
    }
    for relative, content in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    project = ProjectSummary(root=str(tmp_path), files=sorted(files))
    expected = ExpectedResultModel(result_summary="Build DIRI — Developer Intent Reproduction Index")

    score, evidence, missing = evaluate_diri_capabilities(project, expected)

    assert score > 0
    assert "diri/cli.py" in evidence
    assert "Workspace creation" in missing
