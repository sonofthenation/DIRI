from pathlib import Path

from diri.core.models import DeveloperIntent, DiriReport, ExpectedResultModel, MetricScore
from diri.operator.adapters import build_adapters, install_adapters
from diri.operator.packet_builder import build_operator_packet, write_operator_packet
from diri.operator.protocol import render_operator_prompt, write_operator_protocol
from diri.storage.json_store import write_json
from diri.storage.workspace import DiriWorkspace


def test_operator_packet_contains_diri_context(tmp_path: Path) -> None:
    workspace = _workspace_with_report(tmp_path)

    packet = build_operator_packet(tmp_path)

    assert packet["role"] == "DIRI"
    assert packet["mode"] == "temporary_operator_mode"
    assert packet["developer_intent"]["surface_goal"] == "Build DIRI"
    assert packet["latest_report"]["raw_score"] == 80
    assert "Evaluate developer intent reproduction, not generic code quality." in packet["rules"]
    assert workspace.path.exists()


def test_operator_protocol_and_prompt_are_written(tmp_path: Path) -> None:
    _workspace_with_report(tmp_path)

    packet_path = write_operator_packet(tmp_path)
    protocol_path = write_operator_protocol(tmp_path)
    prompt = render_operator_prompt(tmp_path)

    assert packet_path.name == "operator_packet.json"
    assert protocol_path.name == "DIRI_OPERATOR.md"
    assert "Speak as DIRI for this response only" in prompt
    assert "Raw DIRI Score: 80/100" in prompt


def test_install_operator_adapters_writes_bridge_files(tmp_path: Path) -> None:
    adapters = build_adapters("all")
    written = install_adapters(tmp_path, "all")

    assert {adapter.path for adapter in adapters} == {str(path.relative_to(tmp_path)).replace("\\", "/") for path in written}
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".cursor" / "rules" / "diri.mdc").exists()
    assert "temporary DIRI-mode" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")


def _workspace_with_report(path: Path) -> DiriWorkspace:
    workspace = DiriWorkspace(path)
    workspace.ensure_defaults()
    workspace.write_intent(DeveloperIntent(surface_goal="Build DIRI", true_goal="Evaluate intent reproduction", confidence=75))
    workspace.write_expected_result(ExpectedResultModel(result_summary="Build DIRI — Developer Intent Reproduction Index"))
    write_json(workspace.path / "project_summary.json", {"root": str(path), "files": []})
    write_json(
        workspace.reports_path / "latest.json",
        DiriReport(
            raw_score=80,
            trusted_score=60,
            confidence=75,
            level="Strong Reproduction",
            metric_scores={
                "intent_match": MetricScore(
                    name="Intent Match",
                    score=80,
                    reasoning="Intent represented",
                )
            },
        ),
    )
    return workspace
