"""AI Router — registers providers and routes a chat request to the best one.

Providers are built from :class:`Settings`. The router tries the requested
provider, then walks the configured fallback order, skipping any that are not
available (missing key / unreachable base URL).
"""
from __future__ import annotations

from ..config import Settings
from ..logging_setup import get_logger
from .providers import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    OllamaProvider,
    OpenAICompatibleProvider,
    ProviderError,
)

log = get_logger("ai.router")


class AIRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._default_model: str = settings.ai.get("default_model", "gpt-4o-mini")
        self._default_provider: str = settings.ai.get("default_provider", "openrouter")
        self._fallback: list[str] = settings.ai.get("fallback_order", [])
        self._timeout: int = int(settings.ai.get("request_timeout", 60))
        self._providers: dict[str, AIProvider] = {}
        self._build_providers()

    # ------------------------------------------------------------------ setup
    def _build_providers(self) -> None:
        k = self.settings.ai_keys
        model = self._default_model

        self._providers["openai"] = OpenAICompatibleProvider(
            api_key=k.openai, base_url=k.openai_base_url, model=model, timeout=self._timeout
        )
        self._providers["openrouter"] = OpenAICompatibleProvider(
            api_key=k.openrouter,
            base_url="https://openrouter.ai/api/v1",
            model=model,
            timeout=self._timeout,
            extra_headers={"HTTP-Referer": "https://deathbot.local", "X-Title": "DeathBot"},
        )
        self._providers["groq"] = OpenAICompatibleProvider(
            api_key=k.groq, base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant", timeout=self._timeout,
        )
        self._providers["deepseek"] = OpenAICompatibleProvider(
            api_key=k.deepseek, base_url="https://api.deepseek.com/v1",
            model="deepseek-chat", timeout=self._timeout,
        )
        self._providers["ollama"] = OllamaProvider(
            base_url=k.ollama_base_url, timeout=max(self._timeout, 120)
        )

    # --------------------------------------------------------------- querying
    def available_providers(self) -> list[str]:
        return [name for name, p in self._providers.items() if p.available]

    def _resolution_order(self, preferred: str | None) -> list[str]:
        order: list[str] = []
        for name in [preferred, self._default_provider, *self._fallback, *self._providers]:
            if name and name in self._providers and name not in order:
                order.append(name)
        return order

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> ChatResponse:
        errors: list[str] = []
        for name in self._resolution_order(provider):
            candidate = self._providers[name]
            if not candidate.available:
                continue
            try:
                log.info("Routing chat to provider=%s", name)
                return await candidate.chat(messages, model=model)
            except ProviderError as exc:
                errors.append(str(exc))
                log.warning("Provider %s failed: %s", name, exc)

        raise ProviderError(
            "No AI provider could handle the request. "
            + ("Tried: " + "; ".join(errors) if errors else "No providers configured.")
        )
