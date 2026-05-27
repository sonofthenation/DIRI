import os
import stat

from diri.llm.claude_code_provider import ClaudeCodeProvider
from diri.llm.factory import get_intent_provider


def _write_fake_claude(directory) -> None:
    script = directory / "claude"
    script.write_text("#!/usr/bin/env bash\nexit 0\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)


def _isolate_path(tmp_path, monkeypatch) -> None:
    # PATH with no `claude` so auto-detection is deterministic unless we add one.
    monkeypatch.setenv("PATH", str(tmp_path))


def test_disable_flag_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("DIRI_LLM_DISABLE", "1")
    assert get_intent_provider() is None


def test_no_key_and_no_cli_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("DIRI_LLM_DISABLE", raising=False)
    monkeypatch.delenv("DIRI_LLM_BACKEND", raising=False)
    _isolate_path(tmp_path, monkeypatch)
    assert get_intent_provider() is None


def test_auto_falls_back_to_claude_code_when_no_key(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("DIRI_LLM_DISABLE", raising=False)
    monkeypatch.delenv("DIRI_LLM_BACKEND", raising=False)
    _isolate_path(tmp_path, monkeypatch)
    _write_fake_claude(tmp_path)
    provider = get_intent_provider()
    assert isinstance(provider, ClaudeCodeProvider)


def test_backend_off_overrides(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("DIRI_LLM_DISABLE", raising=False)
    monkeypatch.setenv("DIRI_LLM_BACKEND", "off")
    assert get_intent_provider() is None


def test_backend_claude_code_forced(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")  # present, but forced to CLI
    monkeypatch.delenv("DIRI_LLM_DISABLE", raising=False)
    monkeypatch.setenv("DIRI_LLM_BACKEND", "claude-code")
    _isolate_path(tmp_path, monkeypatch)
    _write_fake_claude(tmp_path)
    provider = get_intent_provider()
    assert isinstance(provider, ClaudeCodeProvider)
