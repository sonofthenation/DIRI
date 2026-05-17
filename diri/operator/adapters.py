from dataclasses import dataclass
from pathlib import Path


SUPPORTED_ADAPTERS = ("codex", "claude", "cursor", "windsurf", "gemini", "copilot", "generic", "all")


@dataclass(frozen=True)
class OperatorAdapter:
    name: str
    path: str
    body: str


def build_adapters(target: str = "all") -> list[OperatorAdapter]:
    normalized = target.lower()
    if normalized not in SUPPORTED_ADAPTERS:
        supported = ", ".join(SUPPORTED_ADAPTERS)
        raise ValueError(f"Unsupported operator adapter '{target}'. Supported adapters: {supported}.")

    if normalized == "all":
        names = ("codex", "claude", "cursor", "windsurf", "gemini", "copilot")
    else:
        names = (normalized,)

    return [_adapter_for(name) for name in names]


def install_adapters(project_path: Path, target: str = "all") -> list[Path]:
    written: list[Path] = []
    for adapter in build_adapters(target):
        path = project_path / adapter.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(adapter.body, encoding="utf-8")
        written.append(path)
    return written


def _adapter_for(name: str) -> OperatorAdapter:
    if name in {"codex", "generic"}:
        return OperatorAdapter(name=name, path="AGENTS.md", body=_bridge_body("Codex/OpenCode/Generic agent"))
    if name == "claude":
        return OperatorAdapter(name=name, path="CLAUDE.md", body=_bridge_body("Claude Code"))
    if name == "cursor":
        return OperatorAdapter(name=name, path=".cursor/rules/diri.mdc", body=_bridge_body("Cursor"))
    if name == "windsurf":
        return OperatorAdapter(name=name, path=".windsurf/rules/diri.md", body=_bridge_body("Windsurf"))
    if name == "gemini":
        return OperatorAdapter(name=name, path="GEMINI.md", body=_bridge_body("Gemini CLI"))
    if name == "copilot":
        return OperatorAdapter(
            name=name,
            path=".github/copilot-instructions.md",
            body=_bridge_body("GitHub Copilot"),
        )
    raise ValueError(f"Unsupported operator adapter '{name}'.")


def _bridge_body(agent_name: str) -> str:
    return f"""# DIRI Operator Bridge for {agent_name}

This project uses DIRI — Developer Intent Reproduction Index.

DIRI is not a generic code quality analyzer. DIRI evaluates how well the current codebase reproduces the result the developer intended to achieve.

When the user explicitly asks to run, explain, continue, or act through DIRI:

1. Enter temporary DIRI-mode for that response only.
2. Read `.diri/operator/DIRI_OPERATOR.md`.
3. Use `.diri/operator/operator_packet.json` as the source of truth when it exists.
4. Speak as DIRI, not as the underlying assistant.
5. Evaluate intent reproduction only; do not drift into generic code review.
6. Use evidence from DIRI files and project context. If evidence is missing, say it is missing.
7. Return DIRI-style output: score, meaning, main gaps, next actions, evidence, and confidence notes.
8. After the DIRI response is complete, return to normal assistant mode.

If `.diri/operator/operator_packet.json` is missing, ask the user to run:

```bash
diri operator-packet
```

If `.diri/operator/DIRI_OPERATOR.md` is missing, ask the user to run:

```bash
diri install-operator all
```
"""
