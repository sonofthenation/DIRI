def get_diri_level(score: int) -> str:
    if score <= 30:
        return "Intent Mismatch"
    if score <= 50:
        return "Weak Reproduction"
    if score <= 70:
        return "Partial Reproduction"
    if score <= 85:
        return "Strong Reproduction"
    return "High Fidelity Result"
