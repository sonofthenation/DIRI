from pathlib import Path

from diri.confidence.internal_diri import calculate_internal_diri
from diri.core.models import InternalDiriReport
from diri.scanner.project_scanner import scan_project


def self_score(project_path: str | Path) -> InternalDiriReport:
    return calculate_internal_diri(scan_project(project_path))
