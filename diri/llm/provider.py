class LLMProvider:
    name = "llm"

    def complete_json(self, prompt: str, schema_name: str) -> dict:
        raise NotImplementedError
