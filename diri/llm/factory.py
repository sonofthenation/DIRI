import os
import shutil

from diri.llm.provider import LLMProvider


def _api_provider() -> LLMProvider | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return None
    from diri.llm.anthropic_provider import DEFAULT_MODEL, AnthropicProvider

    return AnthropicProvider(model=os.environ.get("DIRI_LLM_MODEL", DEFAULT_MODEL))


def _claude_code_provider() -> LLMProvider | None:
    binary = os.environ.get("DIRI_CLAUDE_BINARY", "claude")
    if shutil.which(binary) is None:
        return None
    from diri.llm.claude_code_provider import DEFAULT_MODEL, ClaudeCodeProvider

    try:
        timeout = float(os.environ.get("DIRI_LLM_TIMEOUT", "120"))
    except ValueError:
        timeout = 120.0
    return ClaudeCodeProvider(
        model=os.environ.get("DIRI_LLM_MODEL", DEFAULT_MODEL),
        binary=binary,
        timeout=timeout,
    )


def get_intent_provider() -> LLMProvider | None:
    """Select an intent-understanding backend, or None for heuristic mode.

    Resolution order (auto): the Claude API when ANTHROPIC_API_KEY is set and the
    anthropic SDK is installed, otherwise the locally-installed Claude Code CLI
    (reusing its existing subscription login, no API key needed), otherwise None.

    DIRI_LLM_BACKEND forces a choice: "api", "claude-code", or "off".
    DIRI_LLM_DISABLE=1 forces heuristic mode.
    """
    if os.environ.get("DIRI_LLM_DISABLE"):
        return None

    backend = os.environ.get("DIRI_LLM_BACKEND", "auto").strip().lower()
    if backend in ("off", "none", "heuristic"):
        return None
    if backend == "api":
        return _api_provider()
    if backend in ("claude-code", "claude_code", "cli"):
        return _claude_code_provider()

    return _api_provider() or _claude_code_provider()
