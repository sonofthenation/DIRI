import json
from pathlib import Path

from typer.testing import CliRunner

from diri.cli import app


runner = CliRunner()


def _write_report(path: Path, metric_keys: list[str], score: int) -> None:
    report = {
        "raw_score": score,
        "trusted_score": score,
        "confidence": 100,
        "level": "MVP",
        "metric_scores": {
            key: {"name": key.replace("_", " ").title(), "score": score, "reasoning": "", "evidence": []}
            for key in metric_keys
        },
    }
    path.write_text(json.dumps(report), encoding="utf-8")


def test_compare_handles_mismatched_metric_sets(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    _write_report(before, ["intent_match", "completeness"], 60)
    _write_report(after, ["intent_match", "behavioral_reproduction"], 80)

    result = runner.invoke(app, ["compare", str(before), str(after)])

    assert result.exit_code == 0
    assert "Raw score delta: +20" in result.output
    assert "only in before report" in result.output
    assert "only in after report" in result.output


def test_compare_missing_file_reports_clean_error(tmp_path: Path) -> None:
    after = tmp_path / "after.json"
    _write_report(after, ["intent_match"], 80)

    result = runner.invoke(app, ["compare", str(tmp_path / "missing.json"), str(after)])

    assert result.exit_code == 1
    assert "Report not found" in result.output
