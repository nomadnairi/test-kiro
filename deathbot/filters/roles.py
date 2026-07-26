"""Role-based aiogram filters."""
from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from ..container import Container
from ..core.roles import at_least


class IsOwner(BaseFilter):
    async def __call__(self, event: TelegramObject, container: Container) -> bool:
        user = getattr(event, "from_user", None)
        return bool(user and container.access.is_owner(user.id))


class MinRole(BaseFilter):
    def __init__(self, minimum: str) -> None:
        self.minimum = minimum

    async def __call__(self, event: TelegramObject, container: Container,
                       role: str = "guest") -> bool:
        user = getattr(event, "from_user", None)
        if user and container.access.is_owner(user.id):
            return True
        return at_least(role, self.minimum)
