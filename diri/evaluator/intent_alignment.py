from dataclasses import dataclass
from pathlib import Path

from diri.core.models import ExpectedResultModel, ProjectSummary
from diri.evaluator.spec_capabilities import is_diri_spec


@dataclass(frozen=True)
class IntentAlignmentCheck:
    name: str
    path: str
    required_terms: tuple[str, ...]


DIRI_INTENT_ALIGNMENT_CHECKS = (
    IntentAlignmentCheck(
        "Not a generic code quality analyzer",
        "README.md",
        ("not a generic code quality analyzer", "developer intent"),
    ),
    IntentAlignmentCheck(
        "Developer intent data model",
        "diri/core/models.py",
        ("DeveloperIntent", "true_goal", "must_not_have", "confidence"),
    ),
    IntentAlignmentCheck(
        "Expected result data model",
        "diri/core/models.py",
        ("ExpectedResultModel", "success_conditions", "acceptance_criteria"),
    ),
    IntentAlignmentCheck(
        "Intent discovery workflow",
        "diri/intent/intent_discovery.py",
        ("discover_intent", "surface_goal", "true_goal"),
    ),
    IntentAlignmentCheck(
        "Expected result builder workflow",
        "diri/result_model/builder.py",
        ("build_expected_result", "result_summary", "acceptance_criteria"),
    ),
    IntentAlignmentCheck(
        "Evaluation is result-oriented",
        "diri/evaluator/project_evaluator.py",
        ("evaluate_project", "expected", "intent"),
    ),
    IntentAlignmentCheck(
        "LLM prompts preserve project philosophy",
        "diri/llm/prompts.py",
        ("not to evaluate generic code quality", "developer truly wanted"),
    ),
)


def evaluate_intent_alignment(project: ProjectSummary, expected: ExpectedResultModel) -> tuple[int, list[str], list[str]]:
    if not is_diri_spec(expected):
        return 0, [], []

    root = Path(project.root)
    project_files = set(project.files)
    passed = 0
    evidence: list[str] = []
    missing: list[str] = []

    for check in DIRI_INTENT_ALIGNMENT_CHECKS:
        if check.path not in project_files:
            missing.append(check.name)
            continue
        text = _read_text(root / check.path).lower()
        if all(term.lower() in text for term in check.required_terms):
            passed += 1
            evidence.append(check.path)
        else:
            missing.append(check.name)

    score = round((passed / len(DIRI_INTENT_ALIGNMENT_CHECKS)) * 100)
    return score, sorted(set(evidence)), missing


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
