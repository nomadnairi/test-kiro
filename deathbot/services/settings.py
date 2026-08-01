"""SettingsService — per-user preferences."""
from __future__ import annotations

from ..repositories import Repositories

DEFAULTS = {"ai_provider": "", "ai_model": "", "language": "en"}


class SettingsService:
    def __init__(self, repos: Repositories) -> None:
        self.repos = repos

    async def get(self, user_id: int, key: str) -> str | None:
        return await self.repos.settings.get(user_id, key, DEFAULTS.get(key))

    async def set(self, user_id: int, key: str, value: str) -> None:
        await self.repos.settings.set(user_id, key, value)

    async def all(self, user_id: int) -> dict[str, str]:
        stored = await self.repos.settings.all(user_id)
        return {**DEFAULTS, **stored}

    async def reset(self, user_id: int) -> None:
        await self.repos.settings.delete_all(user_id)
