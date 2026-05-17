from diri.core.models import DeveloperIntent


def build_acceptance_criteria(intent: DeveloperIntent) -> list[str]:
    criteria = []
    for item in intent.must_have:
        criteria.append(f"Includes and supports: {item}")
    for item in intent.must_not_have:
        criteria.append(f"Avoids: {item}")
    if intent.true_goal:
        criteria.insert(0, f"Result clearly matches: {intent.true_goal}")
    return criteria
