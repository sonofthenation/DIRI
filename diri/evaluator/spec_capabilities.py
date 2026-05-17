from dataclasses import dataclass, field
from pathlib import Path

from diri.core.models import ExpectedResultModel, ProjectSummary


@dataclass(frozen=True)
class CapabilityCheck:
    name: str
    evidence_paths: tuple[str, ...]
    required_terms: tuple[str, ...] = field(default_factory=tuple)


DIRI_CAPABILITIES = (
    CapabilityCheck("Python project metadata", ("pyproject.toml",), ("typer", "pydantic")),
    CapabilityCheck("Typer CLI entrypoint", ("diri/cli.py",), ("init", "discover", "score", "plan", "self-score", "compare")),
    CapabilityCheck("Pydantic data models", ("diri/core/models.py",), ("DeveloperIntent", "ExpectedResultModel", "DiriReport")),
    CapabilityCheck("DIRI score formula", ("diri/core/scoring.py",), ("calculate_raw_score", "calculate_trusted_score")),
    CapabilityCheck("DIRI score levels", ("diri/core/levels.py",), ("get_diri_level",)),
    CapabilityCheck("Workspace creation", ("diri/storage/workspace.py",), ("intent.json", "expected_result.json", "reports")),
    CapabilityCheck("JSON storage", ("diri/storage/json_store.py",), ("write_json", "read_json")),
    CapabilityCheck("History tracking", ("diri/storage/history.py",), ("append_history",)),
    CapabilityCheck("Project scanner", ("diri/scanner/project_scanner.py",), ("total_files", "total_lines", "tree_summary")),
    CapabilityCheck("File collection ignores", ("diri/scanner/file_collector.py",), ("should_ignore", "collect_files")),
    CapabilityCheck("Language detection", ("diri/scanner/language_detector.py",), ("detect_language",)),
    CapabilityCheck("Intent discovery", ("diri/intent/intent_discovery.py",), ("discover_intent", "DeveloperIntent")),
    CapabilityCheck("Hidden intent detection", ("diri/intent/hidden_intent.py",), ("infer_hidden_intent",)),
    CapabilityCheck("Expected result builder", ("diri/result_model/builder.py",), ("build_expected_result", "ExpectedResultModel")),
    CapabilityCheck("Project evaluator", ("diri/evaluator/project_evaluator.py",), ("evaluate_project",)),
    CapabilityCheck("Metric evaluator", ("diri/evaluator/metric_evaluator.py",), ("evaluate_metrics",)),
    CapabilityCheck("Gap analyzer", ("diri/evaluator/gap_analyzer.py",), ("gaps_from_metrics",)),
    CapabilityCheck("TODO generator", ("diri/planner/todo_generator.py",), ("generate_todo", "TodoItem")),
    CapabilityCheck("Priority engine", ("diri/planner/priority_engine.py",), ("priority_for_severity", "expected_gain")),
    CapabilityCheck("Markdown report", ("diri/report/markdown_report.py",), ("render_markdown_report", "DIRI Report")),
    CapabilityCheck("JSON report", ("diri/report/json_report.py",), ("write_json_report",)),
    CapabilityCheck("Console report", ("diri/report/console_report.py",), ("render_console_report",)),
    CapabilityCheck("Self-score command reuses project scoring", ("diri/cli.py",), ("def self_score_command", "_score_project")),
    CapabilityCheck("Operator Bridge commands", ("diri/cli.py",), ("operator-packet", "operator-prompt", "install-operator")),
    CapabilityCheck("Operator packet builder", ("diri/operator/packet_builder.py",), ("build_operator_packet", "operator_packet.json")),
    CapabilityCheck("Operator protocol", ("diri/operator/protocol.py",), ("DIRI Operator Protocol", "temporary")),
    CapabilityCheck("Operator adapters", ("diri/operator/adapters.py",), ("CLAUDE.md", "AGENTS.md", "GEMINI.md")),
    CapabilityCheck("LLM provider abstraction", ("diri/llm/provider.py", "diri/llm/mock_provider.py"), ("complete_json", "MockProvider")),
    CapabilityCheck("Required examples", ("examples/sample_intent.md", "examples/sample_project/README.md"), ("Developer Intent",)),
    CapabilityCheck(
        "Required test coverage",
        (
            "tests/test_scoring.py",
            "tests/test_levels.py",
            "tests/test_workspace.py",
            "tests/test_todo_generator.py",
            "tests/test_spec_capabilities.py",
        ),
    ),
)


def is_diri_spec(expected: ExpectedResultModel) -> bool:
    text = " ".join(
        [
            expected.result_summary,
            *expected.feature_expectations,
            *expected.acceptance_criteria,
            *expected.runtime_expectations,
        ]
    ).lower()
    return "diri" in text or "developer intent reproduction index" in text


def evaluate_diri_capabilities(project: ProjectSummary, expected: ExpectedResultModel) -> tuple[int, list[str], list[str]]:
    if not is_diri_spec(expected):
        return 0, [], []

    root = Path(project.root)
    project_files = set(project.files)
    passed = 0
    evidence: list[str] = []
    missing: list[str] = []

    for check in DIRI_CAPABILITIES:
        files_present = all(path in project_files for path in check.evidence_paths)
        terms_present = all(_term_exists(root, check.evidence_paths, term) for term in check.required_terms)
        if files_present and terms_present:
            passed += 1
            evidence.extend(check.evidence_paths)
        else:
            missing.append(check.name)

    score = round((passed / len(DIRI_CAPABILITIES)) * 100)
    return score, sorted(set(evidence)), missing


def _term_exists(root: Path, evidence_paths: tuple[str, ...], term: str) -> bool:
    needle = term.lower()
    for relative in evidence_paths:
        path = root / relative
        if not path.exists():
            continue
        try:
            if needle in path.read_text(encoding="utf-8", errors="ignore").lower():
                return True
        except OSError:
            continue
    return False
