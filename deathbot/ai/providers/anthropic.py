"""Anthropic (Claude) provider — the Messages API differs from OpenAI's."""
from __future__ import annotations

import httpx

from .base import AIProvider, ChatMessage, ChatResponse, ProviderError, error_detail


class AnthropicProvider(AIProvider):
    name = "claude"

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest",
                 timeout: int = 60) -> None:
        super().__init__(model=model, timeout=timeout)
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        if not self.available:
            raise ProviderError("claude: missing API key")

        # Anthropic takes the system prompt separately from the message list.
        system = "\n".join(m.content for m in messages if m.role == "system")
        convo = [m.as_dict() for m in messages if m.role in ("user", "assistant")]

        payload = {
            "model": model or self.model,
            "max_tokens": 1024,
            "messages": convo,
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/messages", json=payload, headers=headers)
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"claude: HTTP {exc.response.status_code} — {error_detail(exc.response)}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"claude: {exc}") from exc

        try:
            data = resp.json()
        except ValueError as exc:
            raise ProviderError(f"claude: non-JSON response body: {resp.text[:200]!r}") from exc

        try:
            content = "".join(
                block.get("text", "") for block in data["content"] if block.get("type") == "text"
            )
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"claude: unexpected response shape — {str(data)[:200]}") from exc

        usage = data.get("usage", {})
        tokens = int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))
        return ChatResponse(content=content, provider=self.name,
                            model=payload["model"], tokens=tokens)
