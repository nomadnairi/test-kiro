"""Local Ollama provider (no API key required)."""
from __future__ import annotations

import httpx

from .base import AIProvider, ChatMessage, ChatResponse, ProviderError


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str = "llama3", timeout: int = 120) -> None:
        super().__init__(model=model, timeout=timeout)
        self.base_url = base_url.rstrip("/")

    @property
    def available(self) -> bool:
        return bool(self.base_url)

    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        payload = {
            "model": model or self.model,
            "messages": [m.as_dict() for m in messages],
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"ollama: {exc}") from exc

        content = data.get("message", {}).get("content", "")
        return ChatResponse(content=content, provider=self.name, model=payload["model"])
