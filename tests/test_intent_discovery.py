from diri.intent.intent_discovery import discover_intent


def test_required_features_are_not_misread_as_must_not() -> None:
    notes = """
# Developer Intent

It should not feel like a basic admin panel.

Required features:
- dashboard
- tasks

Must not feel like:
- boring grid
"""

    intent = discover_intent(notes)

    assert "dashboard" in intent.must_have
    assert "tasks" in intent.must_have
    assert "boring grid" in intent.must_not_have
    assert "dashboard" not in intent.must_not_have


def test_diri_spec_true_goal_is_not_taken_from_visual_example() -> None:
    notes = """
# DIRI — Developer Intent Reproduction Index

DIRI is a CLI tool that evaluates how well a codebase reproduces the developer intended result.

Required features:
- score project
- generate TODO tasks

Example:
- premium student planner
"""

    intent = discover_intent(notes)

    assert intent.true_goal == "Measure how well a codebase reproduces the developer's intended result."
    assert "" not in intent.must_have
