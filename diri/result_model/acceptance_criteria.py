from diri.core.models import DeveloperIntent


def build_acceptance_criteria(intent: DeveloperIntent) -> list[str]:
    criteria = []
    for item in _clean_items(intent.must_have):
        criteria.append(f"Includes and supports: {item}")
    for item in _clean_items(intent.must_not_have):
        criteria.append(f"Avoids: {item}")
    if intent.true_goal:
        criteria.insert(0, f"Result clearly matches: {intent.true_goal}")
    return criteria


def _clean_items(items: list[str]) -> list[str]:
    cleaned = []
    for item in items:
        value = item.strip()
        if not value or value == "...":
            continue
        cleaned.append(value)
    return cleaned
