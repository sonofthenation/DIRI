from pathlib import Path

from diri.constants import DEFAULT_WEIGHTS
from diri.core.errors import WorkspaceMissingError
from diri.core.models import DeveloperIntent, ExpectedResultModel, InternalDiriReport
from diri.storage.json_store import read_json, read_model, write_json


class DiriWorkspace:
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path).resolve()
        self.path = self.project_path / ".diri"
        self.reports_path = self.path / "reports"

    def create(self) -> None:
        self.reports_path.mkdir(parents=True, exist_ok=True)

    def require(self) -> None:
        if not self.path.exists():
            raise WorkspaceMissingError(f"No .diri workspace found in {self.project_path}. Run `diri init` first.")

    def write_intent(self, intent: DeveloperIntent) -> None:
        write_json(self.path / "intent.json", intent)

    def read_intent(self) -> DeveloperIntent:
        return read_model(self.path / "intent.json", DeveloperIntent)

    def write_expected_result(self, expected: ExpectedResultModel) -> None:
        write_json(self.path / "expected_result.json", expected)

    def read_expected_result(self) -> ExpectedResultModel:
        return read_model(self.path / "expected_result.json", ExpectedResultModel)

    def write_weights(self) -> None:
        write_json(self.path / "weights.json", DEFAULT_WEIGHTS)

    def read_weights(self) -> dict[str, float]:
        path = self.path / "weights.json"
        if not path.exists():
            return DEFAULT_WEIGHTS
        return {key: float(value) for key, value in read_json(path).items()}

    def write_confidence(self, confidence: InternalDiriReport) -> None:
        write_json(self.path / "confidence.json", confidence)

    def read_confidence(self) -> InternalDiriReport | None:
        path = self.path / "confidence.json"
        if not path.exists():
            return None
        return read_model(path, InternalDiriReport)

    def ensure_defaults(self) -> None:
        self.create()
        if not (self.path / "weights.json").exists():
            self.write_weights()
        if not (self.path / "history.json").exists():
            write_json(self.path / "history.json", [])
        if not (self.path / "preferences.json").exists():
            write_json(self.path / "preferences.json", {"signals": []})
