import json
import os
import stat

import pytest

from diri.llm.claude_code_provider import (
    ClaudeCodeProvider,
    ClaudeCodeUnavailableError,
    _extract_json_object,
)


def _write_fake_claude(directory, body: str) -> None:
    script = directory / "claude"
    script.write_text("#!/usr/bin/env bash\n" + body)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)


def test_extract_json_object_handles_code_fences() -> None:
    text = '```json\n{"surface_goal": "x"}\n```'
    assert _extract_json_object(text) == {"surface_goal": "x"}


def test_extract_json_object_handles_surrounding_prose() -> None:
    text = 'Here is the result:\n{"a": 1}\nDone.'
    assert _extract_json_object(text) == {"a": 1}


def test_provider_parses_cli_envelope(tmp_path, monkeypatch) -> None:
    inner = json.dumps({"surface_goal": "build calm app", "confidence": 80})
    envelope = json.dumps({"type": "result", "is_error": False, "result": inner})
    _write_fake_claude(tmp_path, f"cat >/dev/null\nprintf '%s' '{envelope}'\n")
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    provider = ClaudeCodeProvider()
    result = provider.complete_json("notes", "developer_intent")

    assert result["surface_goal"] == "build calm app"
    assert result["confidence"] == 80


def test_provider_raises_on_cli_failure(tmp_path, monkeypatch) -> None:
    _write_fake_claude(tmp_path, "echo 'boom' >&2\nexit 1\n")
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    provider = ClaudeCodeProvider()
    with pytest.raises(ClaudeCodeUnavailableError):
        provider.complete_json("notes", "developer_intent")


def test_provider_raises_on_error_envelope(tmp_path, monkeypatch) -> None:
    envelope = json.dumps({"type": "result", "is_error": True, "result": "rate limited"})
    _write_fake_claude(tmp_path, f"printf '%s' '{envelope}'\n")
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    provider = ClaudeCodeProvider()
    with pytest.raises(ClaudeCodeUnavailableError):
        provider.complete_json("notes", "developer_intent")


def test_provider_raises_when_binary_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))  # empty dir, no claude
    provider = ClaudeCodeProvider()
    with pytest.raises(ClaudeCodeUnavailableError):
        provider.complete_json("notes", "developer_intent")


def test_provider_command_uses_verified_hardening_flags(tmp_path, monkeypatch) -> None:
    """Regression guard: the CLI 2.1.152 has no --max-turns flag and would error on it.

    Verifies the built argv: --max-turns is absent, the verified hardening flags are
    present, and variadic --tools "" is the last flag (so it cannot eat anything).
    """
    args_log = tmp_path / "args.log"
    envelope = '{"type":"result","is_error":false,"result":"{}"}'
    body = (
        'cat >/dev/null\n'
        f'printf "%s\\n" "$@" >>"{args_log}"\n'
        f"printf '%s' '{envelope}'\n"
    )
    _write_fake_claude(tmp_path, body)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    ClaudeCodeProvider().complete_json("notes", "developer_intent")

    captured = args_log.read_text().splitlines()
    assert "--max-turns" not in captured
    assert "--strict-mcp-config" in captured
    assert "--no-session-persistence" in captured
    assert "--tools" in captured
    assert captured[-2:] == ["--tools", ""]  # variadic flag last, captures only ""
