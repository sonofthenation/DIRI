from diri.llm.provider import LLMProvider


class MockProvider(LLMProvider):
    def __init__(self, responses: dict[str, dict] | None = None):
        self.responses = responses or {}

    def complete_json(self, prompt: str, schema_name: str) -> dict:
        return self.responses.get(schema_name, {})
