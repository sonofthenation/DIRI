from pathlib import Path

from diri.core.models import DeveloperIntent, ProjectSummary
from diri.intent.hidden_intent import infer_hidden_intent
from diri.intent.intent_confidence import estimate_intent_confidence
from diri.llm.provider import LLMProvider

VISUAL_WORDS = {"feel", "visual", "interface", "ui", "ux", "design", "premium", "polished", "layout", "notebook"}
EMOTIONAL_WORDS = {"calm", "academic", "premium", "polished", "rich", "boring", "cheap"}
TECH_WORDS = {"python", "typer", "pydantic", "cli", "json", "markdown", "tests", "llm"}


def read_intent_notes(intent_path: str | Path | None) -> str:
    if not intent_path:
        return ""
    path = Path(intent_path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _clean_bullet(line: str) -> str:
    return line.strip().lstrip("-*").strip()


def _is_meaningful_item(item: str) -> bool:
    cleaned = item.strip()
    if not cleaned:
        return False
    if cleaned in {"...", "----", "---"}:
        return False
    return any(character.isalnum() for character in cleaned)


def discover_intent(
    notes: str,
    project_summary: ProjectSummary | None = None,
    provider: LLMProvider | None = None,
) -> DeveloperIntent:
    return discover_intent_reported(notes, project_summary, provider)[0]


def discover_intent_reported(
    notes: str,
    project_summary: ProjectSummary | None = None,
    provider: LLMProvider | None = None,
) -> tuple[DeveloperIntent, str]:
    """Discover developer intent and report which engine actually produced it.

    Returns (intent, engine_label). The label is the provider's name on success,
    "heuristic (fallback from <name>)" when a configured LLM provider was tried
    but failed, or plain "heuristic" when no provider was given.
    """
    if provider is None:
        return _discover_intent_heuristic(notes, project_summary), "heuristic"
    llm_intent = _discover_intent_llm(notes, project_summary, provider)
    if llm_intent is not None:
        return llm_intent, provider.name
    return _discover_intent_heuristic(notes, project_summary), f"heuristic (fallback from {provider.name})"


def _build_intent_prompt(notes: str, project_summary: ProjectSummary | None) -> str:
    sections = ["Developer intent notes:", notes.strip() or "(none provided)"]
    if project_summary is not None:
        languages = ", ".join(sorted(project_summary.languages)) or "unknown"
        important = "\n".join(f"- {path}" for path in project_summary.important_files[:20])
        sections.append("\nProject context:")
        sections.append(f"Languages: {languages}")
        sections.append(f"Total files: {project_summary.total_files}")
        if important:
            sections.append("Important files:\n" + important)
    return "\n".join(sections)


def _discover_intent_llm(
    notes: str,
    project_summary: ProjectSummary | None,
    provider: LLMProvider,
) -> DeveloperIntent | None:
    try:
        data = provider.complete_json(_build_intent_prompt(notes, project_summary), "developer_intent")
    except Exception:
        return None
    if not data:
        return None
    try:
        intent = DeveloperIntent.model_validate(data)
    except Exception:
        return None
    if not intent.true_goal:
        intent.true_goal = infer_hidden_intent(intent)
    if not intent.confidence:
        intent.confidence = estimate_intent_confidence(intent)
    return intent


def _discover_intent_heuristic(notes: str, project_summary: ProjectSummary | None = None) -> DeveloperIntent:
    lines = [line.strip() for line in notes.splitlines() if line.strip()]
    prose = [line for line in lines if not line.startswith("#")]
    bullets = [_clean_bullet(line) for line in lines if line.startswith(("-", "*"))]

    surface_goal = next((line for line in prose if not line.startswith(("-", "*"))), "")
    functional_target: list[str] = []
    visual_target: list[str] = []
    emotional_target: list[str] = []
    technical_constraints: list[str] = []
    must_not_have: list[str] = []
    must_have: list[str] = []
    preference_signals: list[str] = []
    negative_examples: list[str] = []

    in_must_not = False
    for raw_line in lines:
        lower = raw_line.lower()
        if "required features" in lower or "must have" in lower:
            in_must_not = False
        if "must not" in lower:
            in_must_not = True
        if raw_line.startswith(("-", "*")):
            item = _clean_bullet(raw_line)
            if not _is_meaningful_item(item):
                continue
            item_lower = item.lower()
            if in_must_not:
                must_not_have.append(item)
                negative_examples.append(item)
            else:
                functional_target.append(item)
                must_have.append(item)
            if any(word in item_lower for word in VISUAL_WORDS):
                visual_target.append(item)
            if any(word in item_lower for word in EMOTIONAL_WORDS):
                emotional_target.append(item)
            if any(word in item_lower for word in TECH_WORDS):
                technical_constraints.append(item)
        else:
            if any(word in lower for word in VISUAL_WORDS):
                visual_target.append(raw_line)
                preference_signals.append(raw_line)
            if any(word in lower for word in EMOTIONAL_WORDS):
                emotional_target.append(raw_line)
            if any(word in lower for word in TECH_WORDS):
                technical_constraints.append(raw_line)

    if project_summary and "Python" in project_summary.languages:
        technical_constraints.append("Project includes Python code.")

    intent = DeveloperIntent(
        surface_goal=surface_goal,
        true_goal=surface_goal,
        emotional_target=emotional_target,
        functional_target=functional_target,
        visual_target=visual_target,
        behavioral_target=["The project should behave like the intended product, not just expose disconnected files."],
        technical_constraints=sorted(set(technical_constraints)),
        must_have=must_have,
        must_not_have=must_not_have,
        negative_examples=negative_examples,
        preference_signals=preference_signals,
        unclear_points=[] if surface_goal else ["No explicit developer intent was provided."],
    )
    intent.true_goal = infer_hidden_intent(intent)
    intent.confidence = estimate_intent_confidence(intent)
    return intent
