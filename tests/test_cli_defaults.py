from pathlib import Path

from typer.testing import CliRunner

from diri.cli import app


runner = CliRunner()


def test_init_defaults_to_current_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / ".diri" / "intent.json").exists()
    assert (tmp_path / ".diri" / "expected_result.json").exists()


def test_init_rejects_accidental_package_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "diri"\n', encoding="utf-8")
    package_dir = tmp_path / "diri"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")

    result = runner.invoke(app, ["init", "diri"])

    assert result.exit_code == 1
    assert "looks like the Python package directory" in result.output
    assert not (package_dir / ".diri").exists()
