from diri.constants import MAX_SCORE
from diri.core.models import DeveloperIntent, DiriReport, MetricScore
from diri.core.scoring import calculate_raw_score, calculate_trusted_score, cap_score


def test_max_score_is_below_one_hundred() -> None:
    assert MAX_SCORE < 100


def test_cap_score_never_reaches_one_hundred() -> None:
    assert cap_score(100) == MAX_SCORE
    assert cap_score(150) == MAX_SCORE
    assert cap_score(99) == 99
    assert cap_score(-5) == 0


def test_perfect_inputs_never_yield_one_hundred() -> None:
    perfect = {key: 100 for key in (
        "intent_match",
        "functional_reproduction",
        "behavioral_reproduction",
        "visual_ux_reproduction",
        "constraint_respect",
        "completeness",
    )}
    assert calculate_raw_score(perfect) == MAX_SCORE
    assert calculate_trusted_score(100, 100) == MAX_SCORE


def test_models_cap_perfect_values() -> None:
    assert MetricScore(name="x", score=100, reasoning="r").score == MAX_SCORE
    assert DeveloperIntent(confidence=100.0).confidence == float(MAX_SCORE)
    report = DiriReport(
        raw_score=100,
        trusted_score=100,
        confidence=100,
        level="High Fidelity Result",
        metric_scores={},
    )
    assert report.raw_score == MAX_SCORE
    assert report.trusted_score == MAX_SCORE
    assert report.confidence == MAX_SCORE
