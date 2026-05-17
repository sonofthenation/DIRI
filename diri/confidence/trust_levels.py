def get_trust_level(score: int) -> str:
    if score <= 30:
        return "Experimental"
    if score <= 50:
        return "Prototype"
    if score <= 70:
        return "Usable with Review"
    if score <= 85:
        return "Reliable Assistant"
    return "Trusted Evaluator"
