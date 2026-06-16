from diri.core.models import ProjectSummary
from diri.evaluator.metric_evaluator import _coverage_score


def _project(files: list[str]) -> ProjectSummary:
    return ProjectSummary(root=".", files=files)


def test_coverage_does_not_match_substring_inside_another_word() -> None:
    project = _project(["latest.json", "rapid_client.py"])

    score, evidence = _coverage_score(["test"], project)

    assert score == 10
    assert evidence == []


def test_coverage_matches_whole_word_token() -> None:
    project = _project(["tests/test_scoring.py"])

    score, _ = _coverage_score(["test"], project)

    assert score == 100


def test_coverage_matches_snake_case_token() -> None:
    project = _project(["diri/intent/intent_discovery.py"])

    score, _ = _coverage_score(["intent"], project)

    assert score == 100
