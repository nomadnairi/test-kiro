"""AIService — conversation orchestration on top of the AI router."""
from __future__ import annotations

from ..ai import AIRouter, ChatMessage, ProviderError
from ..config import Settings
from ..repositories import Repositories

_SYSTEM_PROMPT = (
    "You are DeathBot, a concise cybersecurity and OSINT assistant. "
    "Answer clearly. Never invent tool output."
)


class AIService:
    def __init__(self, settings: Settings, repos: Repositories, router: AIRouter) -> None:
        self.settings = settings
        self.repos = repos
        self.router = router
        self.max_history = int(settings.ai.get("max_history", 20))

    def available_providers(self) -> list[str]:
        return self.router.available_providers()

    async def ask(self, user_id: int, prompt: str, *, provider: str | None = None,
                  model: str | None = None) -> str:
        history = await self.repos.history.recent(user_id, self.max_history)
        messages = [ChatMessage("system", _SYSTEM_PROMPT)]
        messages += [ChatMessage(r["role"], r["content"]) for r in history]
        messages.append(ChatMessage("user", prompt))

        await self.repos.history.add(user_id, "user", prompt)
        try:
            response = await self.router.chat(messages, provider=provider, model=model)
        except ProviderError as exc:
            return f"⚠️ AI unavailable: {exc}"

        await self.repos.history.add(
            user_id, "assistant", response.content, response.provider, response.model
        )
        await self.repos.history.record_usage(
            user_id, response.provider, response.model, response.tokens
        )
        return response.content

    async def reset(self, user_id: int) -> None:
        await self.repos.history.clear(user_id)
