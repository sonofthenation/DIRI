from diri.constants import DEFAULT_WEIGHTS


def calculate_raw_score(scores: dict[str, int], weights: dict[str, float] | None = None) -> int:
    active_weights = weights or DEFAULT_WEIGHTS
    total = 0.0

    for key, weight in active_weights.items():
        total += max(0, min(100, scores.get(key, 0))) * weight

    return round(total)


def calculate_trusted_score(raw_score: int, confidence: int) -> int:
    safe_confidence = max(0, min(100, confidence))
    return round(raw_score * (safe_confidence / 100))
