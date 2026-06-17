from diri.core.scoring import calculate_raw_score, calculate_trusted_score


def test_calculate_raw_score_uses_default_weights() -> None:
    scores = {
        "intent_match": 80,
        "functional_reproduction": 70,
        "behavioral_reproduction": 60,
        "visual_ux_reproduction": 50,
        "constraint_respect": 100,
        "completeness": 90,
    }

    assert calculate_raw_score(scores) == 72


def test_calculate_trusted_score_uses_confidence() -> None:
    assert calculate_trusted_score(82, 43) == 35


def test_calculate_raw_score_normalizes_unnormalized_weights() -> None:
    scores = {"a": 100, "b": 0}
    # Weights sum to 4.0; without normalization this would over/underflow the 0-100 range.
    assert calculate_raw_score(scores, {"a": 3.0, "b": 1.0}) == 75


def test_calculate_raw_score_handles_zero_total_weight() -> None:
    assert calculate_raw_score({"a": 100}, {"a": 0.0}) == 0
