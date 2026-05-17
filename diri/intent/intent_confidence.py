from diri.core.models import DeveloperIntent


def estimate_intent_confidence(intent: DeveloperIntent) -> int:
    score = 20
    fields = [
        intent.surface_goal,
        intent.true_goal,
        intent.functional_target,
        intent.visual_target,
        intent.behavioral_target,
        intent.must_have,
        intent.must_not_have,
    ]
    score += sum(8 for value in fields if value)
    if intent.unclear_points:
        score -= min(20, len(intent.unclear_points) * 5)
    return max(0, min(100, score))
