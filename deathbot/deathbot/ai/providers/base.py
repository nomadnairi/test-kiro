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


class AIProvider(abc.ABC):
    name: str = "base"

    def __init__(self, model: str, timeout: int = 60) -> None:
        self.model = model
        self.timeout = timeout

    @property
    @abc.abstractmethod
    def available(self) -> bool:
        """Whether this provider is configured well enough to be called."""

    @abc.abstractmethod
    async def chat(self, messages: list[ChatMessage], *, model: str | None = None) -> ChatResponse:
        ...
