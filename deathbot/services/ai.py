"""AIService — conversation orchestration on top of the AI router.

Per-user API keys added via the bot ("➕ Добавить ключ") are decrypted here and
passed into the router on every call, so a personal key works immediately
without touching .env or restarting the bot.
"""
from __future__ import annotations

from ..ai import AIRouter, ChatMessage, ProviderError
from ..config import Settings
from ..repositories import Repositories
from .apikey import ApiKeyService

_SYSTEM_PROMPT = (
    "Ты DeathBot — лаконичный ассистент по кибербезопасности и OSINT. "
    "Отвечай по-русски, ясно и по делу. Не выдумывай вывод инструментов."
)

# Provider ids the AI router understands — used to filter a user's stored keys
# down to ones that are actually AI providers (they may also have OSINT keys
# like shodan/hibp stored under the same mechanism).
_AI_PROVIDER_IDS = {"openai", "openrouter", "groq", "deepseek", "grok", "claude", "gemini"}


class AIService:
    def __init__(self, settings: Settings, repos: Repositories, router: AIRouter,
                api_keys: ApiKeyService) -> None:
        self.settings = settings
        self.repos = repos
        self.router = router
        self.api_keys = api_keys
        self.max_history = int(settings.ai.get("max_history", 20))

    async def user_keys(self, user_id: int) -> dict[str, str]:
        """Decrypt this user's stored AI-provider keys (if any)."""
        keys: dict[str, str] = {}
        for provider in await self.api_keys.list_providers(user_id):
            if provider not in _AI_PROVIDER_IDS:
                continue
            value = await self.api_keys.get_key(user_id, provider)
            if value:
                keys[provider] = value
        return keys

    async def available_providers(self, user_id: int | None = None) -> list[str]:
        user_keys = await self.user_keys(user_id) if user_id else {}
        return self.router.available_providers(user_keys)

    async def provider_status(self, user_id: int) -> list[dict]:
        return self.router.provider_status(await self.user_keys(user_id))

    async def ask(self, user_id: int, prompt: str, *, provider: str | None = None,
                  model: str | None = None) -> str:
        history = await self.repos.history.recent(user_id, self.max_history)
        messages = [ChatMessage("system", _SYSTEM_PROMPT)]
        messages += [ChatMessage(r["role"], r["content"]) for r in history]
        messages.append(ChatMessage("user", prompt))

        await self.repos.history.add(user_id, "user", prompt)
        try:
            user_keys = await self.user_keys(user_id)
            response = await self.router.chat(
                messages, provider=provider, model=model, user_keys=user_keys,
            )
        except ProviderError as exc:
            return f"⚠️ ИИ недоступен: {exc}"

        await self.repos.history.add(
            user_id, "assistant", response.content, response.provider, response.model
        )
        await self.repos.history.record_usage(
            user_id, response.provider, response.model, response.tokens
        )
        return response.content

    async def reset(self, user_id: int) -> None:
        await self.repos.history.clear(user_id)
