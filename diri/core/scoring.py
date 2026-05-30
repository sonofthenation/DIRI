from diri.constants import DEFAULT_WEIGHTS, MAX_SCORE


def cap_score(value: float) -> int:
    """Clamp any DIRI score into [0, MAX_SCORE].

    DIRI never reports 100% — full intent reproduction is treated as
    unprovable, so every score is hard-capped below 100 at the root.
    """
    return max(0, min(MAX_SCORE, round(value)))


def calculate_raw_score(scores: dict[str, int], weights: dict[str, float] | None = None) -> int:
    active_weights = weights or DEFAULT_WEIGHTS
    total = 0.0

    for key, weight in active_weights.items():
        total += cap_score(scores.get(key, 0)) * weight

    return cap_score(total)


def calculate_trusted_score(raw_score: int, confidence: int) -> int:
    safe_confidence = cap_score(confidence)
    return cap_score(raw_score * (safe_confidence / 100))
