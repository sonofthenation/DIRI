from diri.core.levels import get_diri_level
from diri.core.models import DeveloperIntent, DiriReport, ExpectedResultModel, ProjectSummary
from diri.core.scoring import calculate_raw_score, calculate_trusted_score
from diri.evaluator.gap_analyzer import gaps_from_metrics
from diri.evaluator.metric_evaluator import evaluate_metrics
from diri.planner.todo_generator import generate_todo


def evaluate_project(
    intent: DeveloperIntent,
    expected: ExpectedResultModel,
    project: ProjectSummary,
    weights: dict[str, float] | None = None,
) -> DiriReport:
    metric_scores = evaluate_metrics(intent, expected, project)
    score_values = {key: metric.score for key, metric in metric_scores.items()}
    raw_score = calculate_raw_score(score_values, weights)
    confidence = int(max(0, min(100, intent.confidence)))
    trusted_score = calculate_trusted_score(raw_score, confidence)
    gaps = gaps_from_metrics(metric_scores, expected, project)
    strengths = [metric.name for metric in metric_scores.values() if metric.score >= 70]
    weaknesses = [metric.name for metric in metric_scores.values() if metric.score < 70]
    todo = generate_todo(gaps)
    return DiriReport(
        raw_score=raw_score,
        trusted_score=trusted_score,
        confidence=confidence,
        level=get_diri_level(raw_score),
        metric_scores=metric_scores,
        gaps=gaps,
        strengths=strengths,
        weaknesses=weaknesses,
        todo=todo,
    )
