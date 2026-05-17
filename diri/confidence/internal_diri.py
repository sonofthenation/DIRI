from diri import __version__
from diri.confidence.trust_levels import get_trust_level
from diri.core.models import InternalDiriReport, ProjectSummary


MODULE_FILES = {
    "intent_discovery": ["diri/intent/intent_discovery.py"],
    "hidden_intent_detection": ["diri/intent/hidden_intent.py"],
    "expected_result_modeling": ["diri/result_model/builder.py"],
    "code_to_result_evaluation": ["diri/evaluator/project_evaluator.py", "diri/evaluator/metric_evaluator.py"],
    "gap_analysis": ["diri/evaluator/gap_analyzer.py"],
    "todo_generation": ["diri/planner/todo_generator.py"],
    "preference_memory": ["diri/intent/preference_memory.py"],
    "stability": ["tests/test_scoring.py", "tests/test_levels.py"],
    "explainability": ["diri/report/markdown_report.py", "diri/report/console_report.py"],
    "self_honesty": ["diri/confidence/internal_diri.py", "diri/confidence/self_score.py"],
}

MVP_MATURITY_CAPS = {
    "intent_discovery": 68,
    "hidden_intent_detection": 42,
    "expected_result_modeling": 62,
    "code_to_result_evaluation": 58,
    "gap_analysis": 60,
    "todo_generation": 66,
    "preference_memory": 38,
    "stability": 64,
    "explainability": 64,
    "self_honesty": 72,
}


def calculate_internal_diri(project: ProjectSummary) -> InternalDiriReport:
    files = set(project.files)
    module_scores: dict[str, int] = {}
    for module, expected_files in MODULE_FILES.items():
        present = sum(1 for path in expected_files if path in files)
        base = round((present / len(expected_files)) * 75)
        test_bonus = 15 if any(path.startswith("tests/") for path in files) else 0
        doc_bonus = 10 if "README.md" in files else 0
        structural_score = min(100, base + test_bonus + doc_bonus)
        module_scores[module] = min(structural_score, MVP_MATURITY_CAPS[module])

    confidence_index = round(sum(module_scores.values()) / len(module_scores))
    return InternalDiriReport(
        diri_version=__version__,
        confidence_index=confidence_index,
        trust_level=get_trust_level(confidence_index),
        module_scores=module_scores,
        best_at=[key for key, value in module_scores.items() if value >= 80],
        weak_at=[key for key, value in module_scores.items() if value < 60],
        recommended_use=[
            "Early MVP evaluation of intent-to-result gaps",
            "Generating concrete TODO plans from visible gaps",
        ],
        not_recommended_use=[
            "Unreviewed final judgment on complex products",
            "Replacing human product or design review",
        ],
    )
