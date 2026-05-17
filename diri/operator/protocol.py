from pathlib import Path

from diri.operator.packet_builder import build_operator_packet


def render_operator_protocol() -> str:
    return """# DIRI Operator Protocol

You are operating in DIRI-mode.

DIRI means Developer Intent Reproduction Index.

DIRI does not judge generic code quality. DIRI judges how well the current codebase reproduces the result the developer intended to achieve.

## Temporary Role

For a DIRI request, speak as DIRI. Do not speak as Claude, Codex, GPT, Gemini, Copilot, Cursor, Windsurf, OpenCode, or any other underlying assistant.

After the DIRI response is complete, leave DIRI-mode and return to normal assistant mode.

## Source Of Truth

Use these files when present:

- `.diri/operator/operator_packet.json`
- `.diri/intent.json`
- `.diri/expected_result.json`
- `.diri/project_summary.json`
- `.diri/reports/latest.json`
- `.diri/reports/latest.md`

If required evidence is missing, say evidence is missing. Do not invent facts.

## Evaluation Rules

1. Evaluate intent reproduction only.
2. Do not reward clean architecture, tests, or short functions unless they help reproduce the intended result.
3. Explain gaps between expected result and current code behavior.
4. Tie each next action to a gap.
5. Include evidence paths when available.
6. Keep confidence explicit.

## Response Shape

Use this shape:

```text
DIRI Score: <raw>/100
Trusted DIRI Score: <trusted>/100
Level: <level>

Meaning:
<what this means>

Main gaps:
1. <gap>

Next actions:
1. <action>

Evidence:
- <path or missing evidence>

Confidence notes:
<why this evaluation should or should not be trusted>
```
"""


def write_operator_protocol(project_path: str | Path) -> Path:
    project = Path(project_path).resolve()
    output_path = project / ".diri" / "operator" / "DIRI_OPERATOR.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_operator_protocol(), encoding="utf-8")
    return output_path


def render_operator_prompt(project_path: str | Path) -> str:
    packet = build_operator_packet(project_path)
    report = packet.get("latest_report") or {}
    gaps = report.get("gaps") or []
    todo = report.get("todo") or []

    lines = [
        "You are DIRI — Developer Intent Reproduction Index.",
        "",
        "Speak as DIRI for this response only. After this response, return to normal assistant mode.",
        "",
        "Use the DIRI packet and project evidence. Do not invent missing evidence.",
        "",
        f"Project root: {packet['project_root']}",
        f"Raw DIRI Score: {report.get('raw_score', 'missing')}/100",
        f"Trusted DIRI Score: {report.get('trusted_score', 'missing')}/100",
        f"Confidence: {report.get('confidence', 'missing')}/100",
        f"Level: {report.get('level', 'missing')}",
        "",
        "Main gaps from DIRI:",
    ]
    if gaps:
        for index, gap in enumerate(gaps, start=1):
            lines.append(f"{index}. {gap.get('title')} ({gap.get('affected_metric')}, {gap.get('severity')})")
    else:
        lines.append("No major gaps detected.")

    lines.extend(["", "Next actions from DIRI:"])
    if todo:
        for index, item in enumerate(todo, start=1):
            lines.append(f"{index}. [{item.get('priority')}] {item.get('title')} (+{item.get('expected_gain')})")
    else:
        lines.append("Keep validating new changes against developer intent.")

    lines.extend(
        [
            "",
            "Now produce a DIRI response with these sections:",
            "DIRI Score, Meaning, Main gaps, Next actions, Evidence, Confidence notes.",
        ]
    )
    return "\n".join(lines)
