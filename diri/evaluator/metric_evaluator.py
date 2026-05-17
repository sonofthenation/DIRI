from diri.constants import METRIC_LABELS
from diri.core.models import DeveloperIntent, ExpectedResultModel, MetricScore, ProjectSummary
from diri.evaluator.evidence_collector import find_evidence_for_terms


def _coverage_score(expected_items: list[str], project: ProjectSummary) -> tuple[int, list[str]]:
    if not expected_items:
        return 55, []
    matched = 0
    evidence: list[str] = []
    searchable = " ".join(project.files + list(project.file_summaries.values())).lower()
    for item in expected_items:
        tokens = [token.strip(".,:;!?()[]").lower() for token in item.replace("-", " ").split()]
        meaningful = [token for token in tokens if len(token) >= 4]
        if any(token in searchable for token in meaningful):
            matched += 1
            evidence.extend(find_evidence_for_terms(project, meaningful[:3]))
    score = round((matched / len(expected_items)) * 100)
    return max(10, min(100, score)), sorted(set(evidence))


def evaluate_metrics(intent: DeveloperIntent, expected: ExpectedResultModel, project: ProjectSummary) -> dict[str, MetricScore]:
    feature_score, feature_evidence = _coverage_score(expected.feature_expectations, project)
    ux_score, ux_evidence = _coverage_score(expected.ux_expectations, project)
    criteria_score, criteria_evidence = _coverage_score(expected.acceptance_criteria, project)

    has_workspace = ".diri/intent.json" in project.files and ".diri/expected_result.json" in project.files
    has_reports = any(path.startswith(".diri/reports/") for path in project.files)
    has_cli = any(path.endswith("cli.py") or "cli" in path.lower() for path in project.files)
    has_tests = any(path.startswith("tests/") for path in project.files)
    has_docs = any(path.lower().endswith("readme.md") for path in project.files)

    intent_score = round((intent.confidence * 0.65) + (criteria_score * 0.35))
    behavior_score = 40 + (20 if has_cli else 0) + (15 if has_workspace else 0) + (10 if has_reports else 0) + (10 if has_tests else 0)
    constraint_score = 50 + (15 if has_docs else 0) + (15 if has_tests else 0) + (20 if "Python" in project.languages else 0)
    completeness_score = round((feature_score * 0.45) + (behavior_score * 0.30) + (constraint_score * 0.25))

    values = {
        "intent_match": (
            intent_score,
            "Intent model has enough explicit signals to evaluate the project." if intent_score >= 70 else "Intent model is still thin or acceptance signals are weak.",
            criteria_evidence,
        ),
        "functional_reproduction": (
            feature_score,
            "Expected features are represented in the project files." if feature_score >= 70 else "Several expected features are not visible in the codebase map.",
            feature_evidence,
        ),
        "behavioral_reproduction": (
            min(100, behavior_score),
            "Project has executable/workspace/reporting behavior." if behavior_score >= 70 else "Executable behavior or persisted reporting is incomplete.",
            project.important_files[:8],
        ),
        "visual_ux_reproduction": (
            ux_score,
            "Visual/UX intent appears represented in files or notes." if ux_score >= 70 else "Visual/UX expectations are weakly represented in the current codebase.",
            ux_evidence,
        ),
        "constraint_respect": (
            min(100, constraint_score),
            "Project respects core technical shape expected by the spec." if constraint_score >= 70 else "Project is missing expected technical signals such as docs, tests, or Python package structure.",
            project.important_files[:8],
        ),
        "completeness": (
            max(0, min(100, completeness_score)),
            "Implementation looks complete enough for MVP use." if completeness_score >= 70 else "Implementation is not yet complete against expected result and command surface.",
            sorted(set(feature_evidence + project.important_files[:5])),
        ),
    }

    return {
        key: MetricScore(name=METRIC_LABELS[key], score=int(score), reasoning=reasoning, evidence=evidence)
        for key, (score, reasoning, evidence) in values.items()
    }
