from diri.confidence.trust_levels import get_trust_level
from diri.core.levels import get_diri_level


def test_diri_levels() -> None:
    assert get_diri_level(30) == "Intent Mismatch"
    assert get_diri_level(50) == "Weak Reproduction"
    assert get_diri_level(70) == "Partial Reproduction"
    assert get_diri_level(85) == "Strong Reproduction"
    assert get_diri_level(86) == "High Fidelity Result"


def test_trust_levels() -> None:
    assert get_trust_level(30) == "Experimental"
    assert get_trust_level(50) == "Prototype"
    assert get_trust_level(70) == "Usable with Review"
    assert get_trust_level(85) == "Reliable Assistant"
    assert get_trust_level(86) == "Trusted Evaluator"
