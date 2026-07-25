"""Per-user key/value settings."""
from __future__ import annotations

from .base import BaseRepository


class SettingsRepository(BaseRepository):
    async def get(self, user_id: int, key: str, default: str | None = None) -> str | None:
        row = await self.db.fetch_one(
            "SELECT value FROM settings WHERE user_id = ? AND key = ?", (user_id, key)
        )
        return row["value"] if row else default

    async def set(self, user_id: int, key: str, value: str) -> None:
        await self.db.execute(
            "INSERT INTO settings (user_id, key, value) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value",
            (user_id, key, value),
        )

    async def all(self, user_id: int) -> dict[str, str]:
        rows = await self.db.fetch_all(
            "SELECT key, value FROM settings WHERE user_id = ?", (user_id,)
        )
        return {r["key"]: r["value"] for r in rows}
