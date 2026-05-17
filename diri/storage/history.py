from datetime import datetime, timezone
from pathlib import Path

from diri.storage.json_store import read_json, write_json


def append_history(workspace_path: Path, event: str, payload: dict) -> None:
    history_path = workspace_path / "history.json"
    history = read_json(history_path) if history_path.exists() else []
    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": payload,
        }
    )
    write_json(history_path, history)
