from diri.constants import DEFAULT_WEIGHTS


def calculate_raw_score(scores: dict[str, int], weights: dict[str, float] | None = None) -> int:
    active_weights = weights or DEFAULT_WEIGHTS
    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        return 0

    total = 0.0
    for key, weight in active_weights.items():
        normalized_weight = weight / total_weight
        total += max(0, min(100, scores.get(key, 0))) * normalized_weight

    return round(total)


def calculate_trusted_score(raw_score: int, confidence: int) -> int:
    safe_confidence = max(0, min(100, confidence))
    return round(raw_score * (safe_confidence / 100))
