from diri.core.models import DeveloperIntent


def infer_hidden_intent(intent: DeveloperIntent) -> str:
    explicit = f"{intent.surface_goal} {' '.join(intent.technical_constraints)}".lower()
    if "developer intent reproduction index" in explicit or "diri" in explicit:
        return "Measure how well a codebase reproduces the developer's intended result."

    signals = " ".join(intent.visual_target + intent.emotional_target + intent.preference_signals).lower()
    if any(word in signals for word in ["premium", "polished", "rich", "calm"]):
        return "The developer likely wants a finished product experience, not merely working screens."
    if intent.functional_target and not intent.true_goal:
        return "The developer likely wants the listed features to form a coherent end-to-end result."
    return intent.true_goal or intent.surface_goal
