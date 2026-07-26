"""Structured logging of every incoming event."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from ..logging_setup import get_logger

log = get_logger("mw.logging")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        text = getattr(event, "text", None)
        log.info("event user=%s text=%r", getattr(user, "id", None), text)
        return await handler(event, data)
