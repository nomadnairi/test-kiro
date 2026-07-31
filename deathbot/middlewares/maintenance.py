"""Maintenance gate — during maintenance only the owner may interact."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, User

from ..container import Container


class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        container: Container = data["container"]
        if not container.settings.maintenance:
            return await handler(event, data)

        user: User | None = data.get("event_from_user")
        if user and container.access.is_owner(user.id):
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer("🛠 DeathBot на техобслуживании. Загляни позже.")
        return None
