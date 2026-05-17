from diri.core.models import ExpectedResultModel, Gap, MetricScore, ProjectSummary


def gaps_from_metrics(metrics: dict[str, MetricScore], expected: ExpectedResultModel, project: ProjectSummary) -> list[Gap]:
    gaps: list[Gap] = []
    for key, metric in metrics.items():
        if metric.score >= 70:
            continue
        severity = "high" if metric.score < 45 else "medium"
        expected_text = expected.result_summary or ", ".join(expected.acceptance_criteria[:2]) or "developer intent reproduction"
        gaps.append(
            Gap(
                title=f"{metric.name} below target",
                expected=expected_text,
                actual=metric.reasoning,
                severity=severity,
                affected_metric=key,
                evidence=metric.evidence or project.important_files[:5],
            )
        )
    return gaps
