from diri.llm.provider import LLMProvider


class OpenAIProvider(LLMProvider):
    def complete_json(self, prompt: str, schema_name: str) -> dict:
        raise NotImplementedError("OpenAI provider is reserved for a later DIRI stage.")
