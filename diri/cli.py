from pathlib import Path

import typer

from diri.core.errors import DiriError
from diri.core.models import DiriReport
from diri.evaluator.project_evaluator import evaluate_project
from diri.intent.intent_discovery import discover_intent_reported, read_intent_notes
from diri.intent.preference_memory import update_preference_memory
from diri.llm.factory import get_intent_provider
from diri.operator.adapters import SUPPORTED_ADAPTERS, install_adapters
from diri.operator.packet_builder import write_operator_packet
from diri.operator.protocol import render_operator_prompt, write_operator_protocol
from diri.report.console_report import render_console_report
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
def init(
    project: Path = typer.Argument(Path("."), help="Project directory to initialize. Defaults to current directory."),
    intent: Path | None = typer.Option(None, "--intent", "-i", help="Path to intent.md"),
) -> None:
    """Create a .diri workspace and initial intent/result models."""
    try:
        project_path = _resolve_project_path(project)
        _guard_accidental_package_init(project_path)
        project_path.mkdir(parents=True, exist_ok=True)
        workspace = DiriWorkspace(project_path)
        workspace.ensure_defaults()
        summary = scan_project(project_path)
        write_json(workspace.path / "project_summary.json", summary)
        notes = read_intent_notes(intent)
        provider = get_intent_provider()
        developer_intent, engine = discover_intent_reported(notes, summary, provider)
        expected = build_expected_result(developer_intent)
        workspace.write_intent(developer_intent)
        workspace.write_expected_result(expected)
        update_preference_memory(workspace.path, developer_intent.preference_signals)
        append_history(workspace.path, "init", {"project": str(project_path), "intent": str(intent) if intent else None})
        typer.echo(f"Initialized DIRI workspace: {workspace.path}")
        typer.echo(f"Intent engine: {engine}")
        typer.echo(f"Intent confidence: {int(developer_intent.confidence)}/100")
    except DiriError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command()
def discover(
    project: Path = typer.Argument(Path("."), help="Project directory. Defaults to current directory."),
    intent: Path | None = typer.Option(None, "--intent", "-i", help="Path to intent.md"),
) -> None:
    """Re-discover developer intent and update workspace models."""
    project_path = _resolve_project_path(project)
    workspace = DiriWorkspace(project_path)
    workspace.require()
    summary = scan_project(project_path)
    notes = read_intent_notes(intent)
    provider = get_intent_provider()
    developer_intent, engine = discover_intent_reported(notes, summary, provider)
    expected = build_expected_result(developer_intent)
    workspace.write_intent(developer_intent)
    workspace.write_expected_result(expected)
    write_json(workspace.path / "project_summary.json", summary)
    update_preference_memory(workspace.path, developer_intent.preference_signals)
    append_history(workspace.path, "discover", {"confidence": int(developer_intent.confidence)})
    typer.echo(f"Intent engine: {engine}")
    typer.echo(f"Intent confidence: {int(developer_intent.confidence)}/100")
    if developer_intent.unclear_points:
        typer.echo("Unclear points:")
        for point in developer_intent.unclear_points:
            typer.echo(f"- {point}")


@app.command()
def score(project: Path = typer.Argument(Path("."), help="Project directory. Defaults to current directory.")) -> None:
    """Score a project against its .diri intent and expected result."""
    report = _score_project(_resolve_project_path(project))
    typer.echo(render_console_report(report))


@app.command()
def plan(project: Path = typer.Argument(Path("."), help="Project directory. Defaults to current directory.")) -> None:
    """Generate a TODO plan from the latest DIRI report."""
    project_path = _resolve_project_path(project)
    workspace = DiriWorkspace(project_path)
    workspace.require()
    latest_path = workspace.reports_path / "latest.json"
    if not latest_path.exists():
        report = _score_project(project_path)
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
    """Run DIRI's normal project scoring flow on DIRI itself."""
    project_root = Path(__file__).resolve().parents[1]
    try:
        report = _score_project(project_root)
    except DiriError as exc:
        typer.echo(str(exc), err=True)
        typer.echo("Initialize DIRI itself first, for example: diri init . --intent path/to/DIRI_Technical_Spec.md", err=True)
        raise typer.Exit(1)
    typer.echo(render_console_report(report))


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


@app.command("operator-packet")
def operator_packet(
    project: Path = typer.Argument(Path("."), help="Project directory. Defaults to current directory."),
) -> None:
    """Write .diri/operator/operator_packet.json for LLM operators."""
    project_path = _resolve_project_path(project)
    workspace = DiriWorkspace(project_path)
    workspace.require()
    if not (workspace.reports_path / "latest.json").exists():
        _score_project(project_path)
    packet_path = write_operator_packet(project_path)
    protocol_path = write_operator_protocol(project_path)
    append_history(workspace.path, "operator-packet", {"packet": str(packet_path), "protocol": str(protocol_path)})
    typer.echo(f"Wrote operator packet: {packet_path}")
    typer.echo(f"Wrote operator protocol: {protocol_path}")


@app.command("operator-prompt")
def operator_prompt(
    project: Path = typer.Argument(Path("."), help="Project directory. Defaults to current directory."),
) -> None:
    """Print a copy-paste DIRI prompt for any LLM operator."""
    project_path = _resolve_project_path(project)
    workspace = DiriWorkspace(project_path)
    workspace.require()
    if not (workspace.reports_path / "latest.json").exists():
        _score_project(project_path)
    write_operator_packet(project_path)
    write_operator_protocol(project_path)
    typer.echo(render_operator_prompt(project_path))


@app.command("install-operator")
def install_operator(
    target: str = typer.Argument("all", help=f"Adapter to install: {', '.join(SUPPORTED_ADAPTERS)}."),
    project: Path = typer.Option(Path("."), "--project", "-p", help="Project directory. Defaults to current directory."),
) -> None:
    """Install DIRI Operator Bridge files for local AI coding agents."""
    project_path = _resolve_project_path(project)
    workspace = DiriWorkspace(project_path)
    workspace.require()
    if not (workspace.reports_path / "latest.json").exists():
        _score_project(project_path)
    packet_path = write_operator_packet(project_path)
    protocol_path = write_operator_protocol(project_path)
    try:
        adapter_paths = install_adapters(project_path, target)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)
    append_history(
        workspace.path,
        "install-operator",
        {
            "target": target,
            "packet": str(packet_path),
            "protocol": str(protocol_path),
            "adapters": [str(path) for path in adapter_paths],
        },
    )
    typer.echo(f"Wrote operator packet: {packet_path}")
    typer.echo(f"Wrote operator protocol: {protocol_path}")
    for path in adapter_paths:
        typer.echo(f"Installed adapter: {path}")


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


def _resolve_project_path(project: Path | None) -> Path:
    return (project or Path(".")).resolve()


def _guard_accidental_package_init(project_path: Path) -> None:
    parent_pyproject = project_path.parent / "pyproject.toml"
    if not (project_path / "__init__.py").exists() or not parent_pyproject.exists():
        return

    pyproject_text = parent_pyproject.read_text(encoding="utf-8", errors="ignore").lower()
    if f'name = "{project_path.name.lower()}"' not in pyproject_text:
        return

    raise DiriError(
        f"{project_path} looks like the Python package directory, not the project root. "
        "Run `diri init .` from the repository root instead."
    )


if __name__ == "__main__":
    app()
