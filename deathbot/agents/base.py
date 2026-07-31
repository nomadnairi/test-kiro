"""AI agents — thin, prompt-specialised wrappers over the AI router.

Each agent has a system persona and a `run` that turns a task string into a
model call. Agents are deliberately simple; tool-calling orchestration can be
layered on top later via the TaskEngine.
"""
from __future__ import annotations

from ..ai import AIRouter, ChatMessage, ProviderError


class Agent:
    name: str = "agent"
    persona: str = "You are a helpful assistant."

    def __init__(self, router: AIRouter) -> None:
        self.router = router

    async def run(self, task: str, *, provider: str | None = None) -> str:
        messages = [
            ChatMessage("system", self.persona),
            ChatMessage("user", task),
        ]
        try:
            resp = await self.router.chat(messages, provider=provider)
            return resp.content
        except ProviderError as exc:
            return f"⚠️ Агент «{self.name}» недоступен: {exc}"
