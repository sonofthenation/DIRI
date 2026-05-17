from diri.constants import METRIC_LABELS
from diri.core.models import DeveloperIntent, ExpectedResultModel, MetricScore, ProjectSummary
from diri.evaluator.evidence_collector import find_evidence_for_terms
from diri.evaluator.intent_alignment import evaluate_intent_alignment
from diri.evaluator.report_experience import evaluate_report_experience
from diri.evaluator.spec_capabilities import evaluate_diri_capabilities


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
    capability_score, capability_evidence, missing_capabilities = evaluate_diri_capabilities(project, expected)
    if capability_score > feature_score:
        feature_score = capability_score
        feature_evidence = capability_evidence
    ux_score, ux_evidence = _coverage_score(expected.ux_expectations, project)
    report_ux_score, report_ux_evidence, missing_report_ux = evaluate_report_experience(project, expected)
    if report_ux_score > ux_score:
        ux_score = report_ux_score
        ux_evidence = report_ux_evidence
    criteria_score, criteria_evidence = _coverage_score(expected.acceptance_criteria, project)

    has_workspace = ".diri/intent.json" in project.files and ".diri/expected_result.json" in project.files
    has_reports = any(path.startswith(".diri/reports/") for path in project.files)
    has_cli = any(path.endswith("cli.py") or "cli" in path.lower() for path in project.files)
    has_tests = any(path.startswith("tests/") for path in project.files)
    has_docs = any(path.lower().endswith("readme.md") for path in project.files)

    intent_score = round((intent.confidence * 0.65) + (criteria_score * 0.35))
    alignment_score, alignment_evidence, missing_alignment = evaluate_intent_alignment(project, expected)
    if alignment_score > intent_score:
        intent_score = alignment_score
        criteria_evidence = alignment_evidence
    behavior_score = 40 + (20 if has_cli else 0) + (15 if has_workspace else 0) + (10 if has_reports else 0) + (10 if has_tests else 0)
    constraint_score = 50 + (15 if has_docs else 0) + (15 if has_tests else 0) + (20 if "Python" in project.languages else 0)
    completeness_score = round((feature_score * 0.45) + (behavior_score * 0.30) + (constraint_score * 0.25))

    values = {
        "intent_match": (
            intent_score,
            _intent_reasoning(intent_score, missing_alignment),
            criteria_evidence,
        ),
        "functional_reproduction": (
            feature_score,
            _functional_reasoning(feature_score, missing_capabilities),
            feature_evidence,
        ),
        "behavioral_reproduction": (
            min(100, behavior_score),
            "Project has executable/workspace/reporting behavior." if behavior_score >= 70 else "Executable behavior or persisted reporting is incomplete.",
            project.important_files[:8],
        ),
        "visual_ux_reproduction": (
            ux_score,
            _ux_reasoning(ux_score, missing_report_ux),
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


def _functional_reasoning(score: int, missing_capabilities: list[str]) -> str:
    if missing_capabilities and score < 70:
        missing = ", ".join(missing_capabilities[:4])
        return f"Required DIRI capabilities are incomplete: {missing}."
    if missing_capabilities:
        missing = ", ".join(missing_capabilities[:3])
        return f"Most required DIRI capabilities are present; remaining gaps: {missing}."
    if score >= 70:
        return "Required DIRI capabilities are represented by concrete project modules."
    return "Several expected features are not visible in the codebase map."


def _intent_reasoning(score: int, missing_alignment: list[str]) -> str:
    if missing_alignment and score < 70:
        missing = ", ".join(missing_alignment[:4])
        return f"DIRI intent alignment is incomplete: {missing}."
    if missing_alignment:
        missing = ", ".join(missing_alignment[:3])
        return f"DIRI intent is mostly represented; remaining gaps: {missing}."
    if score >= 70:
        return "The project explicitly represents the Developer Intent Reproduction Index philosophy."
    return "Intent model is still thin or acceptance signals are weak."


def _ux_reasoning(score: int, missing_report_ux: list[str]) -> str:
    if missing_report_ux and score < 70:
        missing = ", ".join(missing_report_ux[:4])
        return f"Report experience is incomplete: {missing}."
    if missing_report_ux:
        missing = ", ".join(missing_report_ux[:3])
        return f"Report experience is mostly clear; remaining gaps: {missing}."
    if score >= 70:
        return "CLI and Markdown reports provide a clear user-facing evaluation experience."
    return "Visual/UX expectations are weakly represented in the current codebase."
