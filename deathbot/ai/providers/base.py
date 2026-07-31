"""Provider abstraction for the AI router."""
from __future__ import annotations

import abc
from dataclasses import dataclass


class ProviderError(RuntimeError):
    """Raised when a provider cannot fulfil a request."""


@dataclass(slots=True)
class ChatMessage:
    role: str  # system | user | assistant
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(slots=True)
class ChatResponse:
    content: str
    provider: str
    model: str
    tokens: int = 0


def error_detail(resp, limit: int = 300) -> str:
    """Pull the vendor's own error message out of an HTTP error response body.

    A bare status code ("HTTP 404") is nearly useless for diagnosing API
    errors — OpenRouter/OpenAI/Anthropic/Gemini/etc. put the actual reason
    (invalid model, no credits, data-policy opt-in required, rate limited…)
    in a JSON body that was previously discarded entirely.
    """
    try:
        data = resp.json()
        err = data.get("error")
        if isinstance(err, dict):
            msg = err.get("message") or err.get("code") or str(err)
        elif err:
            msg = str(err)
        else:
            msg = data.get("message") or resp.text
    except ValueError:
        msg = resp.text
    msg = (msg or "no details in response body").strip()
    return msg if len(msg) <= limit else msg[:limit] + "…"


class AIProvider(abc.ABC):
    name: str = "base"

    def __init__(self, model: str, timeout: int = 60, name: str | None = None) -> None:
        self.model = model
        self.timeout = timeout
        if name:
            # Per-instance override — needed because several vendors (OpenAI,
            # OpenRouter, Groq, DeepSeek, Grok, LM Studio, AnythingLLM) all
            # share the OpenAICompatibleProvider class; without this every
            # error message would say "openai-compatible" and be useless for
            # telling which one actually failed.
            self.name = name

    @property
    @abc.abstractmethod
    def available(self) -> bool:
        """Whether this provider is configured well enough to be called."""

    @abc.abstractmethod
    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        ...
