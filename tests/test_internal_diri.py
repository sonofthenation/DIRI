from diri.confidence.internal_diri import calculate_internal_diri
from diri.core.models import ProjectSummary


def test_internal_diri_scores_known_modules() -> None:
    project = ProjectSummary(
        root=".",
        files=[
            "README.md",
            "diri/intent/intent_discovery.py",
            "diri/result_model/builder.py",
            "diri/evaluator/project_evaluator.py",
            "diri/evaluator/metric_evaluator.py",
            "tests/test_scoring.py",
            "tests/test_levels.py",
        ],
    )

    report = calculate_internal_diri(project)

    assert report.confidence_index > 0
    assert "intent_discovery" in report.module_scores
