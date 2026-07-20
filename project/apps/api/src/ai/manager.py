from __future__ import annotations

from collections.abc import AsyncGenerator

from src.ai.protocols import AIProvider, Message
from src.ai.providers import (
    AnthropicProvider,
    GeminiProvider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)


class AIManager:
    def __init__(self, primary: AIProvider, fallback: AIProvider | None = None):
        self.primary = primary
        self.fallback = fallback

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        try:
            response = await self.primary.generate(messages, temperature, max_tokens)
            return response.content
        except Exception:
            if self.fallback is None:
                raise
            response = await self.fallback.generate(messages, temperature, max_tokens)
            return response.content

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.primary.generate_stream(messages, temperature, max_tokens):
                yield chunk
        except Exception:
            if self.fallback is None:
                raise
            async for chunk in self.fallback.generate_stream(messages, temperature, max_tokens):
                yield chunk


def get_ai_manager(provider_name: str | None = None) -> AIManager:
    from src.core.config import settings

    name = (provider_name or settings.AI_DEFAULT_PROVIDER).lower()
    primary = _build_provider(name)
    fallback_name = settings.AI_FALLBACK_PROVIDER
    fallback = _build_provider(fallback_name) if fallback_name else None
    return AIManager(primary, fallback)


def _build_provider(name: str) -> AIProvider:
    if name == "openai":
        return OpenAIProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    if name == "ollama":
        return OllamaProvider()
    return MockProvider()
