import json
import os
import shutil
import subprocess

from diri.llm.prompts import INTENT_DISCOVERY_PROMPT
from diri.llm.provider import LLMProvider

DEFAULT_MODEL = "claude-opus-4-7"

_JSON_ONLY_INSTRUCTION = (
    "\n\nReturn ONLY a single JSON object that matches the fields described above. "
    "No markdown, no code fences, no commentary before or after the JSON."
)

_SYSTEM_PROMPTS: dict[str, str] = {
    "developer_intent": INTENT_DISCOVERY_PROMPT,
}


class ClaudeCodeUnavailableError(RuntimeError):
    """Raised when the local Claude Code CLI cannot be used."""


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
        text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ClaudeCodeUnavailableError("Claude Code returned no JSON object.")
        data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ClaudeCodeUnavailableError("Claude Code returned non-object JSON.")
    return data


class ClaudeCodeProvider(LLMProvider):
    """LLMProvider that drives the locally-installed Claude Code CLI.

    Uses the user's existing Claude Code login (subscription) via the official
    `claude` binary in headless print mode, so no ANTHROPIC_API_KEY is required.
    """

    name = "Claude Code (local CLI)"

    def __init__(self, model: str = DEFAULT_MODEL, binary: str = "claude", timeout: float = 120.0):
        self.model = model
        self.binary = binary
        self.timeout = timeout

    def complete_json(self, prompt: str, schema_name: str) -> dict:
        system_prompt = _SYSTEM_PROMPTS.get(schema_name)
        if system_prompt is None:
            raise ClaudeCodeUnavailableError(f"No system prompt registered for '{schema_name}'.")

        binary = shutil.which(self.binary)
        if binary is None:
            raise ClaudeCodeUnavailableError(
                f"The '{self.binary}' CLI was not found on PATH. Install Claude Code to use this engine."
            )

        cmd = [
            binary,
            "-p",
            "--output-format",
            "json",
            "--model",
            self.model,
            "--append-system-prompt",
            system_prompt + _JSON_ONLY_INSTRUCTION,
            "--max-turns",
            "1",
        ]

        # Force the CLI to use its own stored login: a stray ANTHROPIC_API_KEY
        # would otherwise take precedence over the subscription.
        env = dict(os.environ)
        env.pop("ANTHROPIC_API_KEY", None)

        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise ClaudeCodeUnavailableError("Claude Code timed out.") from exc

        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()[:200]
            raise ClaudeCodeUnavailableError(f"claude exited {proc.returncode}: {detail}")

        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ClaudeCodeUnavailableError("Could not parse Claude Code JSON envelope.") from exc

        if envelope.get("is_error"):
            raise ClaudeCodeUnavailableError(f"Claude Code reported an error: {envelope.get('result', '')[:200]}")

        return _extract_json_object(envelope.get("result", ""))
