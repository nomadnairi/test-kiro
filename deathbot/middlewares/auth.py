"""Auth middleware — upserts the user and puts their role into handler data."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from ..container import Container


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None:
            container: Container = data["container"]
            role = await container.access.register_seen(
                user.id, user.username, user.full_name
            )
            data["role"] = role
        return await handler(event, data)
