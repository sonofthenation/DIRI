def priority_for_severity(severity: str) -> str:
    if severity == "high":
        return "high"
    if severity == "medium":
        return "medium"
    return "low"


def expected_gain_for_severity(severity: str) -> int:
    if severity == "high":
        return 12
    if severity == "medium":
        return 7
    return 3
