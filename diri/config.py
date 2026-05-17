from pathlib import Path

from diri.constants import DEFAULT_WORKSPACE_DIR


def workspace_path(project_path: str | Path) -> Path:
    return Path(project_path).resolve() / DEFAULT_WORKSPACE_DIR
