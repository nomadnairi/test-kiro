"""Access / whitelist queries (thin view over the users table)."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class AccessRepository(BaseRepository):
    async def is_whitelisted(self, user_id: int) -> bool:
        row = await self.db.fetch_one(
            "SELECT 1 FROM users WHERE id = ? AND is_active = 1 AND is_banned = 0",
            (user_id,),
        )
        return row is not None

    async def get_role(self, user_id: int) -> str | None:
        row = await self.db.fetch_one("SELECT role FROM users WHERE id = ?", (user_id,))
        return row["role"] if row else None

    async def list_by_role(self, role: str) -> list[sqlite3.Row]:
        return await self.db.fetch_all("SELECT * FROM users WHERE role = ?", (role,))
