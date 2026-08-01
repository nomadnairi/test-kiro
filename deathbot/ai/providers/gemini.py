"""Google Gemini provider — generateContent REST API."""
from __future__ import annotations

import httpx

from .base import AIProvider, ChatMessage, ChatResponse, ProviderError, error_detail


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash",
                 timeout: int = 60) -> None:
        super().__init__(model=model, timeout=timeout)
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        if not self.available:
            raise ProviderError("gemini: missing API key")

        model_id = model or self.model
        contents = []
        system_bits = []
        for m in messages:
            if m.role == "system":
                system_bits.append(m.content)
                continue
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict = {"contents": contents}
        if system_bits:
            payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_bits)}]}

        url = f"{self.base_url}/models/{model_id}:generateContent?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"gemini: HTTP {exc.response.status_code} — {error_detail(exc.response)}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"gemini: {exc}") from exc

        try:
            data = resp.json()
        except ValueError as exc:
            raise ProviderError(f"gemini: non-JSON response body: {resp.text[:200]!r}") from exc

        block_reason = data.get("promptFeedback", {}).get("blockReason")
        if block_reason:
            raise ProviderError(f"gemini: request blocked by safety filter ({block_reason})")

        try:
            parts = data["candidates"][0]["content"]["parts"]
            content = "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError) as exc:
            finish_reason = (data.get("candidates") or [{}])[0].get("finishReason")
            reason = f" (finishReason={finish_reason})" if finish_reason else ""
            raise ProviderError(
                f"gemini: unexpected response shape{reason} — {str(data)[:200]}"
            ) from exc

        return ChatResponse(content=content, provider=self.name, model=model_id)
