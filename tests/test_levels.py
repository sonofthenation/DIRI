from diri.core.levels import get_diri_level


def test_diri_levels() -> None:
    assert get_diri_level(30) == "Intent Mismatch"
    assert get_diri_level(50) == "Weak Reproduction"
    assert get_diri_level(70) == "Partial Reproduction"
    assert get_diri_level(85) == "Strong Reproduction"
    assert get_diri_level(86) == "High Fidelity Result"
