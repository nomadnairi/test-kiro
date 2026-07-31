"""In-memory sliding-window rate limiter (per user)."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, User

from ..container import Container


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        container: Container = data["container"]
        if user is None or container.access.is_owner(user.id):
            return await handler(event, data)

        cfg = container.settings.ratelimit
        window = float(cfg.get("window_seconds", 10))
        limit = int(cfg.get("max_requests", 20))

        now = time.monotonic()
        bucket = self._hits[user.id]
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            if isinstance(event, Message):
                await event.answer("⏳ Слишком часто — подожди немного.")
            return None

        bucket.append(now)
        return await handler(event, data)
