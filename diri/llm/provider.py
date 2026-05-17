class LLMProvider:
    def complete_json(self, prompt: str, schema_name: str) -> dict:
        raise NotImplementedError
