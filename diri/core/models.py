from typing import Any

from pydantic import BaseModel, Field


class DeveloperIntent(BaseModel):
    surface_goal: str = ""
    true_goal: str = ""
    emotional_target: list[str] = Field(default_factory=list)
    functional_target: list[str] = Field(default_factory=list)
    visual_target: list[str] = Field(default_factory=list)
    behavioral_target: list[str] = Field(default_factory=list)
    technical_constraints: list[str] = Field(default_factory=list)
    must_have: list[str] = Field(default_factory=list)
    must_not_have: list[str] = Field(default_factory=list)
    negative_examples: list[str] = Field(default_factory=list)
    preference_signals: list[str] = Field(default_factory=list)
    unclear_points: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class ExpectedResultModel(BaseModel):
    result_summary: str = ""
    success_conditions: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    feature_expectations: list[str] = Field(default_factory=list)
    ux_expectations: list[str] = Field(default_factory=list)
    architecture_expectations: list[str] = Field(default_factory=list)
    runtime_expectations: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class MetricScore(BaseModel):
    name: str
    score: int
    reasoning: str
    evidence: list[str] = Field(default_factory=list)


class Gap(BaseModel):
    title: str
    expected: str
    actual: str
    severity: str
    affected_metric: str
    evidence: list[str] = Field(default_factory=list)


class TodoItem(BaseModel):
    priority: str
    title: str
    reason: str
    target_metric: str
    expected_gain: int = 0
    files_to_check: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class DiriReport(BaseModel):
    raw_score: int
    trusted_score: int
    confidence: int
    level: str
    metric_scores: dict[str, MetricScore]
    gaps: list[Gap] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    todo: list[TodoItem] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    root: str
    files: list[str] = Field(default_factory=list)
    languages: dict[str, int] = Field(default_factory=dict)
    important_files: list[str] = Field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    tree_summary: str = ""
    file_summaries: dict[str, str] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    metric_scores: dict[str, MetricScore]
    gaps: list[Gap] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


def model_to_dict(model: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(model, BaseModel):
        return model.model_dump(mode="json")
    return model
