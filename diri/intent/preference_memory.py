from pathlib import Path

from diri.storage.json_store import read_json, write_json


def update_preference_memory(workspace_path: Path, signals: list[str]) -> None:
    path = workspace_path / "preferences.json"
    existing = read_json(path) if path.exists() else {"signals": []}
    merged = sorted(set(existing.get("signals", []) + signals))
    write_json(path, {"signals": merged})
