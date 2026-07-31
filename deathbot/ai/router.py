"""AI Router — registers providers and routes a chat request to the best one.

Providers are built from :class:`Settings` (.env-configured, shared by every
user). On top of that, callers can pass ``user_keys`` — a per-user map of
provider id → API key, decrypted from the database — which take priority: if a
user added their own OpenRouter/OpenAI/Claude/etc. key via the bot, it is used
instead of (or in addition to) whatever is configured in .env, without needing
a restart or an admin to touch the deployment's environment.

The router tries the requested provider, then the user's own keys, then the
configured fallback order, skipping anything that isn't available.
"""
from __future__ import annotations

from typing import Callable

from ..config import Settings
from ..logging_setup import get_logger
from .providers import (
    AIProvider,
    AnthropicProvider,
    ChatMessage,
    ChatResponse,
    GeminiProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    ProviderError,
)

log = get_logger("ai.router")

# Providers with a real per-account API key can be overridden per user.
# Local/self-hosted servers (Ollama, LM Studio, AnythingLLM) are deployment-wide
# infrastructure, not a personal account, so they stay .env-only.
_USER_OVERRIDABLE = {"openai", "openrouter", "groq", "deepseek", "grok", "claude", "gemini"}


class AIRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._default_provider: str = settings.ai.get("default_provider", "openrouter")
        self._fallback: list[str] = settings.ai.get("fallback_order", [])
        self._timeout: int = int(settings.ai.get("request_timeout", 60))
        self._providers: dict[str, AIProvider] = {}
        self._builders: dict[str, Callable[[str], AIProvider]] = {}
        self._models: dict[str, str] = {}
        self._build_providers()

    # ------------------------------------------------------------------ setup
    def _register(self, provider_id: str, factory: Callable[[str], AIProvider],
                  default_key: str, model: str) -> None:
        """Register a provider that can be rebuilt with a different API key."""
        self._builders[provider_id] = factory
        self._providers[provider_id] = factory(default_key)
        self._models[provider_id] = model

    def _build_providers(self) -> None:
        k = self.settings.ai_keys
        t = self._timeout

        self._register("openai", lambda key: OpenAICompatibleProvider(
            name="openai", api_key=key, base_url=k.openai_base_url,
            model=k.openai_model, timeout=t,
        ), k.openai, k.openai_model)

        self._register("openrouter", lambda key: OpenAICompatibleProvider(
            name="openrouter", api_key=key, base_url="https://openrouter.ai/api/v1",
            model=k.openrouter_model, timeout=t,
            extra_headers={"HTTP-Referer": "https://deathbot.local", "X-Title": "DeathBot"},
        ), k.openrouter, k.openrouter_model)

        self._register("groq", lambda key: OpenAICompatibleProvider(
            name="groq", api_key=key, base_url="https://api.groq.com/openai/v1",
            model=k.groq_model, timeout=t,
        ), k.groq, k.groq_model)

        self._register("deepseek", lambda key: OpenAICompatibleProvider(
            name="deepseek", api_key=key, base_url="https://api.deepseek.com/v1",
            model=k.deepseek_model, timeout=t,
        ), k.deepseek, k.deepseek_model)

        self._register("grok", lambda key: OpenAICompatibleProvider(
            name="grok", api_key=key, base_url="https://api.x.ai/v1",
            model=k.grok_model, timeout=t,
        ), k.grok, k.grok_model)

        self._register("claude", lambda key: AnthropicProvider(
            api_key=key, model=k.anthropic_model, timeout=t,
        ), k.anthropic, k.anthropic_model)

        self._register("gemini", lambda key: GeminiProvider(
            api_key=key, model=k.gemini_model, timeout=t,
        ), k.gemini, k.gemini_model)

        # Local / self-hosted — .env only, no per-user override, opt-in via URL.
        self._providers["lmstudio"] = OpenAICompatibleProvider(
            name="lmstudio",
            api_key=("lm-studio" if k.lmstudio_base_url else ""),  # server ignores the value
            base_url=k.lmstudio_base_url, model=k.lmstudio_model, timeout=max(t, 120),
        )
        self._models["lmstudio"] = k.lmstudio_model

        self._providers["anythingllm"] = OpenAICompatibleProvider(
            name="anythingllm", api_key=k.anythingllm, base_url=k.anythingllm_base_url,
            model=k.anythingllm_model, timeout=t,
        )
        self._models["anythingllm"] = k.anythingllm_model

        self._providers["ollama"] = OllamaProvider(
            base_url=k.ollama_base_url, model=k.ollama_model, timeout=max(t, 120),
        )
        self._models["ollama"] = k.ollama_model

    # --------------------------------------------------------------- querying
    def available_providers(self, user_keys: dict[str, str] | None = None) -> list[str]:
        user_keys = user_keys or {}
        return [name for name, p in self._providers.items()
                if p.available or name in user_keys]

    def provider_status(self, user_keys: dict[str, str] | None = None) -> list[dict]:
        """Per-provider diagnostics for the "🤖 Провайдеры" button / --check."""
        user_keys = user_keys or {}
        rows = []
        for name, p in self._providers.items():
            has_user_key = name in user_keys
            if has_user_key:
                source = "личный ключ"
            elif p.available:
                source = "ключ в .env" if name in _USER_OVERRIDABLE else "локальный сервер"
            else:
                source = "—"
            rows.append({
                "name": name,
                "available": p.available or has_user_key,
                "source": source,
                "model": self._models.get(name, p.model),
                "personal_key_supported": name in _USER_OVERRIDABLE,
            })
        return rows

    def _resolution_order(self, preferred: str | None, user_keys: dict[str, str]) -> list[str]:
        order: list[str] = []
        # A provider the user personally configured a key for should win over
        # the deployment's own default — that's almost always their intent.
        candidates = [preferred, *user_keys.keys(), self._default_provider,
                      *self._fallback, *self._providers]
        for name in candidates:
            if name and name in self._providers and name not in order:
                order.append(name)
        return order

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        provider: str | None = None,
        model: str | None = None,
        user_keys: dict[str, str] | None = None,
    ) -> ChatResponse:
        user_keys = user_keys or {}
        errors: list[str] = []
        for name in self._resolution_order(provider, user_keys):
            user_key = user_keys.get(name)
            builder = self._builders.get(name)
            candidate = builder(user_key) if (user_key and builder) else self._providers[name]
            if not candidate.available:
                continue
            try:
                log.info("Routing chat to provider=%s (personal_key=%s)",
                        name, bool(user_key))
                return await candidate.chat(messages, model=model)
            except ProviderError as exc:
                errors.append(str(exc))
                log.warning("Provider %s failed: %s", name, exc)

        raise ProviderError(
            "No AI provider could handle the request. "
            + ("Tried: " + "; ".join(errors) if errors else "No providers configured.")
        )
