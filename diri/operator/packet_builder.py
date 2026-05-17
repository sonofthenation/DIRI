from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from diri.core.models import DiriReport
from diri.storage.json_store import read_json, read_model, write_json
from diri.storage.workspace import DiriWorkspace


def build_operator_packet(project_path: str | Path) -> dict[str, Any]:
    project = Path(project_path).resolve()
    workspace = DiriWorkspace(project)
    workspace.require()

    latest_report_path = workspace.reports_path / "latest.json"
    latest_report = read_model(latest_report_path, DiriReport) if latest_report_path.exists() else None
    project_summary_path = workspace.path / "project_summary.json"

    return {
        "schema": "diri.operator_packet.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "role": "DIRI",
        "mode": "temporary_operator_mode",
        "project_root": str(project),
        "source_files": {
            "intent": ".diri/intent.json",
            "expected_result": ".diri/expected_result.json",
            "project_summary": ".diri/project_summary.json",
            "latest_report": ".diri/reports/latest.json",
        },
        "rules": [
            "Speak as DIRI only while answering a DIRI evaluation request.",
            "Return to normal assistant mode after the DIRI response.",
            "Do not answer as Claude, Codex, GPT, Gemini, Copilot, Cursor, Windsurf, or OpenCode during DIRI-mode.",
            "Evaluate developer intent reproduction, not generic code quality.",
            "Use only the supplied DIRI context and explicit project evidence.",
            "If evidence is missing, say evidence is missing.",
            "Do not invent files, runtime behavior, or user intent.",
        ],
        "output_contract": {
            "required_sections": [
                "DIRI Score",
                "Meaning",
                "Main Gaps",
                "Next Actions",
                "Evidence",
                "Confidence Notes",
            ],
            "style": "concise, direct, evidence-grounded, DIRI voice",
        },
        "developer_intent": workspace.read_intent().model_dump(mode="json"),
        "expected_result": workspace.read_expected_result().model_dump(mode="json"),
        "project_summary": read_json(project_summary_path) if project_summary_path.exists() else {},
        "latest_report": latest_report.model_dump(mode="json") if latest_report else {},
    }


def write_operator_packet(project_path: str | Path) -> Path:
    project = Path(project_path).resolve()
    packet = build_operator_packet(project)
    output_path = project / ".diri" / "operator" / "operator_packet.json"
    write_json(output_path, packet)
    return output_path
