import os

from diri.llm.provider import LLMProvider


def get_intent_provider() -> LLMProvider | None:
    """Return a Claude-backed provider when available, else None for heuristic mode.

    Returns None (rather than raising) when DIRI_LLM_DISABLE is set, no
    ANTHROPIC_API_KEY is present, or the anthropic SDK is not installed.
    """
    if os.environ.get("DIRI_LLM_DISABLE"):
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None

    try:
        import anthropic  # noqa: F401
    except ImportError:
        return None

    from diri.llm.anthropic_provider import DEFAULT_MODEL, AnthropicProvider

    model = os.environ.get("DIRI_LLM_MODEL", DEFAULT_MODEL)
    return AnthropicProvider(model=model)
