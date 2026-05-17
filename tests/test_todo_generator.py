from diri.core.models import Gap
from diri.planner.todo_generator import generate_todo


def test_todo_generator_turns_gap_into_actionable_task() -> None:
    todo = generate_todo(
        [
            Gap(
                title="Visual identity mismatch",
                expected="premium notebook UI",
                actual="generic dashboard",
                severity="high",
                affected_metric="visual_ux_reproduction",
                evidence=["templates/dashboard.html"],
            )
        ]
    )

    assert todo[0].priority == "high"
    assert todo[0].expected_gain == 12
    assert todo[0].target_metric == "visual_ux_reproduction"
    assert todo[0].files_to_check == ["templates/dashboard.html"]
