"""OpenAI-compatible chat provider.

Covers OpenAI, OpenRouter, Groq, DeepSeek and LM Studio — they all speak the
same ``/chat/completions`` contract, differing only in base URL / key / default
model. Concrete providers are thin subclasses that set those.
"""
from __future__ import annotations

import httpx

from ...logging_setup import get_logger
from .base import AIProvider, ChatMessage, ChatResponse, ProviderError, error_detail

log = get_logger("ai.openai")


class OpenAICompatibleProvider(AIProvider):
    name = "openai-compatible"  # overridden per instance — see __init__

    def __init__(self, api_key: str, base_url: str, model: str,
                 timeout: int = 60, extra_headers: dict[str, str] | None = None,
                 name: str | None = None) -> None:
        super().__init__(model=model, timeout=timeout, name=name)
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
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"{self.name}: HTTP {exc.response.status_code} — "
                f"{error_detail(exc.response)}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.name}: {exc}") from exc

        try:
            data = resp.json()
        except ValueError as exc:
            raise ProviderError(
                f"{self.name}: non-JSON response body: {resp.text[:200]!r}"
            ) from exc

        # Gateways like OpenRouter can answer HTTP 200 with an {"error": {...}}
        # body instead of "choices" when model routing fails after the
        # handshake (e.g. no endpoints available for that model/data policy) —
        # surface that specific reason rather than a bare "malformed response".
        if isinstance(data, dict) and data.get("error"):
            raise ProviderError(f"{self.name}: {error_detail(resp)}")

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                f"{self.name}: unexpected response shape — {str(data)[:200]}"
            ) from exc

        tokens = int(data.get("usage", {}).get("total_tokens", 0) or 0)
        return ChatResponse(
            content=content, provider=self.name, model=payload["model"], tokens=tokens
        )
