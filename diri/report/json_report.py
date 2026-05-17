from pathlib import Path

from diri.core.models import DiriReport
from diri.storage.json_store import write_json


def write_json_report(report: DiriReport, path: Path) -> None:
    write_json(path, report)
