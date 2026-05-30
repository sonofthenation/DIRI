from diri.intent.intent_discovery import discover_intent, discover_intent_reported
from diri.llm.mock_provider import MockProvider
from diri.llm.provider import LLMProvider


class RaisingProvider(LLMProvider):
    def complete_json(self, prompt: str, schema_name: str) -> dict:
        raise RuntimeError("API exploded")


def test_llm_provider_intent_is_used() -> None:
    provider = MockProvider(
        {
            "developer_intent": {
                "surface_goal": "Build a calm note-taking app",
                "true_goal": "A focused writing space that feels like paper",
                "functional_target": ["editor", "tags"],
                "confidence": 77,
            }
        }
    )

    intent = discover_intent("any notes", None, provider)

    assert intent.surface_goal == "Build a calm note-taking app"
    assert intent.functional_target == ["editor", "tags"]
    assert int(intent.confidence) == 77


def test_llm_missing_true_goal_and_confidence_are_filled() -> None:
    provider = MockProvider(
        {"developer_intent": {"surface_goal": "ship a dashboard", "functional_target": ["charts"]}}
    )

    intent = discover_intent("notes", None, provider)

    assert intent.true_goal  # derived via infer_hidden_intent
    assert intent.confidence > 0  # derived via estimate_intent_confidence


def test_llm_failure_falls_back_to_heuristic() -> None:
    notes = """
Required features:
- dashboard

Must not feel like:
- boring grid
"""

    intent = discover_intent(notes, None, RaisingProvider())

    assert "dashboard" in intent.must_have
    assert "boring grid" in intent.must_not_have


def test_empty_llm_response_falls_back_to_heuristic() -> None:
    provider = MockProvider({})

    intent = discover_intent("Required features:\n- tasks", None, provider)

    assert "tasks" in intent.must_have


def test_reported_label_no_provider_is_heuristic() -> None:
    _, engine = discover_intent_reported("notes", None, None)
    assert engine == "heuristic"


def test_reported_label_on_success_is_provider_name() -> None:
    provider = MockProvider({"developer_intent": {"surface_goal": "x", "confidence": 50}})
    _, engine = discover_intent_reported("notes", None, provider)
    assert engine == provider.name


def test_reported_label_on_failure_shows_fallback() -> None:
    _, engine = discover_intent_reported("notes", None, RaisingProvider())
    assert engine.startswith("heuristic (fallback from ")
