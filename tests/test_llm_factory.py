from diri.llm.factory import get_intent_provider


def test_no_api_key_returns_none(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("DIRI_LLM_DISABLE", raising=False)
    assert get_intent_provider() is None


def test_disable_flag_returns_none(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("DIRI_LLM_DISABLE", "1")
    assert get_intent_provider() is None
