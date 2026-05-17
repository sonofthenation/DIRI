from diri.core.models import DeveloperIntent, ExpectedResultModel
from diri.storage.workspace import DiriWorkspace


def test_workspace_creates_expected_files(tmp_path) -> None:
    workspace = DiriWorkspace(tmp_path)
    workspace.ensure_defaults()
    workspace.write_intent(DeveloperIntent(surface_goal="Build a useful CLI", confidence=70))
    workspace.write_expected_result(ExpectedResultModel(result_summary="Useful CLI"))

    assert (tmp_path / ".diri" / "intent.json").exists()
    assert (tmp_path / ".diri" / "expected_result.json").exists()
    assert (tmp_path / ".diri" / "weights.json").exists()
    assert workspace.read_intent().surface_goal == "Build a useful CLI"
