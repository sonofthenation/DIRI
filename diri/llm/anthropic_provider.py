from typing import Type

from pydantic import BaseModel

from diri.core.models import DeveloperIntent
from diri.llm.prompts import INTENT_DISCOVERY_PROMPT
from diri.llm.provider import LLMProvider

DEFAULT_MODEL = "claude-opus-4-7"

_SCHEMAS: dict[str, tuple[Type[BaseModel], str]] = {
    "developer_intent": (DeveloperIntent, INTENT_DISCOVERY_PROMPT),
}


class LLMUnavailableError(RuntimeError):
    """Raised when the Claude backend cannot be used (missing SDK or API key)."""


class AnthropicProvider(LLMProvider):
    """LLMProvider backed by the Claude API via the official anthropic SDK."""

    name = "Claude (API)"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, max_tokens: int = 4096):
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens

    def complete_json(self, prompt: str, schema_name: str) -> dict:
        if schema_name not in _SCHEMAS:
            raise LLMUnavailableError(f"No structured schema registered for '{schema_name}'.")
        output_model, system_prompt = _SCHEMAS[schema_name]

        try:
            import anthropic
        except ImportError as exc:
            raise LLMUnavailableError(
                "The anthropic SDK is not installed. Install it with: pip install 'diri[llm]'."
            ) from exc

        client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else anthropic.Anthropic()

        response = client.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
            output_format=output_model,
        )
        parsed = response.parsed_output
        if parsed is None:
            raise LLMUnavailableError("Claude returned no structured output.")
        return parsed.model_dump(mode="json")
