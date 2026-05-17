from pathlib import Path

import typer

from diri.confidence.self_score import self_score as calculate_self_score
from diri.core.errors import DiriError
from diri.core.models import DiriReport
from diri.evaluator.project_evaluator import evaluate_project
from diri.intent.intent_discovery import discover_intent, read_intent_notes
from diri.intent.preference_memory import update_preference_memory
from diri.report.console_report import render_console_report, render_internal_report
from diri.report.json_report import write_json_report
from diri.report.markdown_report import render_markdown_report
from diri.result_model.builder import build_expected_result
from diri.scanner.project_scanner import scan_project
from diri.storage.history import append_history
from diri.storage.json_store import read_model, write_json
from diri.storage.workspace import DiriWorkspace

app = typer.Typer(help="DIRI — Developer Intent Reproduction Index")


@app.callback()
def main() -> None:
    """Evaluate how well code reproduces developer intent."""


@app.command()
def init(project: Path, intent: Path | None = typer.Option(None, "--intent", "-i", help="Path to intent.md")) -> None:
    """Create a .diri workspace and initial intent/result models."""
    try:
        project_path = project.resolve()
        project_path.mkdir(parents=True, exist_ok=True)
        workspace = DiriWorkspace(project_path)
        workspace.ensure_defaults()
        summary = scan_project(project_path)
        write_json(workspace.path / "project_summary.json", summary)
        notes = read_intent_notes(intent)
        developer_intent = discover_intent(notes, summary)
        expected = build_expected_result(developer_intent)
        workspace.write_intent(developer_intent)
        workspace.write_expected_result(expected)
        internal = calculate_self_score(Path(__file__).resolve().parents[1])
        workspace.write_confidence(internal)
        update_preference_memory(workspace.path, developer_intent.preference_signals)
        append_history(workspace.path, "init", {"project": str(project_path), "intent": str(intent) if intent else None})
        typer.echo(f"Initialized DIRI workspace: {workspace.path}")
        typer.echo(f"Intent confidence: {int(developer_intent.confidence)}/100")
    except DiriError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command()
def discover(project: Path, intent: Path | None = typer.Option(None, "--intent", "-i", help="Path to intent.md")) -> None:
    """Re-discover developer intent and update workspace models."""
    workspace = DiriWorkspace(project)
    workspace.require()
    summary = scan_project(project)
    notes = read_intent_notes(intent)
    developer_intent = discover_intent(notes, summary)
    expected = build_expected_result(developer_intent)
    workspace.write_intent(developer_intent)
    workspace.write_expected_result(expected)
    write_json(workspace.path / "project_summary.json", summary)
    update_preference_memory(workspace.path, developer_intent.preference_signals)
    append_history(workspace.path, "discover", {"confidence": int(developer_intent.confidence)})
    typer.echo(f"Intent confidence: {int(developer_intent.confidence)}/100")
    if developer_intent.unclear_points:
        typer.echo("Unclear points:")
        for point in developer_intent.unclear_points:
            typer.echo(f"- {point}")


@app.command()
def score(project: Path) -> None:
    """Score a project against its .diri intent and expected result."""
    report = _score_project(project)
    typer.echo(render_console_report(report))


@app.command()
def plan(project: Path) -> None:
    """Generate a TODO plan from the latest DIRI report."""
    workspace = DiriWorkspace(project)
    workspace.require()
    latest_path = workspace.reports_path / "latest.json"
    if not latest_path.exists():
        report = _score_project(project)
    else:
        report = read_model(latest_path, DiriReport)
    if not report.todo:
        typer.echo("No TODO items generated. Current report has no major gaps.")
        return
    for item in report.todo:
        typer.echo(f"[{item.priority}] {item.title} (+{item.expected_gain})")
        typer.echo(f"  {item.reason}")


@app.command("self-score")
def self_score_command() -> None:
    """Evaluate DIRI itself and print the DIRI Confidence Index."""
    project_root = Path(__file__).resolve().parents[1]
    report = calculate_self_score(project_root)
    workspace = DiriWorkspace(project_root)
    workspace.ensure_defaults()
    workspace.write_confidence(report)
    typer.echo(render_internal_report(report))


@app.command()
def compare(before: Path, after: Path) -> None:
    """Compare two JSON DIRI reports."""
    before_report = read_model(before, DiriReport)
    after_report = read_model(after, DiriReport)
    typer.echo(f"Raw score delta: {after_report.raw_score - before_report.raw_score:+}")
    typer.echo(f"Trusted score delta: {after_report.trusted_score - before_report.trusted_score:+}")
    typer.echo("Metric deltas:")
    for key, before_metric in before_report.metric_scores.items():
        after_metric = after_report.metric_scores[key]
        typer.echo(f"- {after_metric.name}: {after_metric.score - before_metric.score:+}")


def _score_project(project: Path) -> DiriReport:
    workspace = DiriWorkspace(project)
    workspace.require()
    summary = scan_project(project)
    write_json(workspace.path / "project_summary.json", summary)
    report = evaluate_project(
        workspace.read_intent(),
        workspace.read_expected_result(),
        summary,
        workspace.read_weights(),
    )
    workspace.reports_path.mkdir(parents=True, exist_ok=True)
    write_json_report(report, workspace.reports_path / "latest.json")
    (workspace.reports_path / "latest.md").write_text(render_markdown_report(report), encoding="utf-8")
    append_history(workspace.path, "score", {"raw_score": report.raw_score, "trusted_score": report.trusted_score})
    return report


if __name__ == "__main__":
    app()
