from diri.core.models import Gap, TodoItem
from diri.planner.priority_engine import expected_gain_for_severity, priority_for_severity


def generate_todo(gaps: list[Gap]) -> list[TodoItem]:
    items: list[TodoItem] = []
    for gap in gaps:
        priority = priority_for_severity(gap.severity)
        items.append(
            TodoItem(
                priority=priority,
                title=f"Close gap: {gap.title}",
                reason=f"Expected {gap.expected}, but found {gap.actual}.",
                target_metric=gap.affected_metric,
                expected_gain=expected_gain_for_severity(gap.severity),
                files_to_check=gap.evidence,
                acceptance_criteria=[
                    f"The reported gap is no longer present: {gap.title}",
                    f"{gap.affected_metric} score improves in the next DIRI report.",
                ],
            )
        )
    return items
