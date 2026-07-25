"""OpenAI-compatible chat provider.

Covers OpenAI, OpenRouter, Groq, DeepSeek and LM Studio — they all speak the
same ``/chat/completions`` contract, differing only in base URL / key / default
model. Concrete providers are thin subclasses that set those.
"""
from __future__ import annotations

import httpx

from ...logging_setup import get_logger
from .base import AIProvider, ChatMessage, ChatResponse, ProviderError

log = get_logger("ai.openai")


class OpenAICompatibleProvider(AIProvider):
    name = "openai-compatible"

    def __init__(self, api_key: str, base_url: str, model: str,
                 timeout: int = 60, extra_headers: dict[str, str] | None = None) -> None:
        super().__init__(model=model, timeout=timeout)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.extra_headers = extra_headers or {}

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.base_url)

    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        if not self.available:
            raise ProviderError(f"{self.name}: missing API key")

        headers = {"Authorization": f"Bearer {self.api_key}", **self.extra_headers}
        payload = {
            "model": model or self.model,
            "messages": [m.as_dict() for m in messages],
        }
        url = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"{self.name}: HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.name}: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"{self.name}: malformed response") from exc

        tokens = int(data.get("usage", {}).get("total_tokens", 0) or 0)
        return ChatResponse(
            content=content, provider=self.name, model=payload["model"], tokens=tokens
        )
