"""User persistence."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> sqlite3.Row | None:
        return await self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    async def upsert(self, user_id: int, username: str | None, full_name: str | None,
                     role: str | None = None, is_active: int = 1) -> None:
        existing = await self.get(user_id)
        if existing is None:
            await self.db.execute(
                "INSERT INTO users (id, username, full_name, role, is_active) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, username, full_name, role or "guest", is_active),
            )
        else:
            await self.db.execute(
                "UPDATE users SET username = ?, full_name = ?, last_seen_at = datetime('now') "
                "WHERE id = ?",
                (username, full_name, user_id),
            )

    async def set_role(self, user_id: int, role: str) -> None:
        await self.db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))

    async def set_banned(self, user_id: int, banned: bool) -> None:
        await self.db.execute(
            "UPDATE users SET is_banned = ? WHERE id = ?", (1 if banned else 0, user_id)
        )

    async def set_active(self, user_id: int, active: bool) -> None:
        await self.db.execute(
            "UPDATE users SET is_active = ? WHERE id = ?", (1 if active else 0, user_id)
        )

    async def touch(self, user_id: int) -> None:
        await self.db.execute(
            "UPDATE users SET last_seen_at = datetime('now') WHERE id = ?", (user_id,)
        )

    async def list_all(self, limit: int = 100) -> list[sqlite3.Row]:
        return await self.db.fetch_all(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ?", (limit,)
        )

    async def count(self) -> int:
        row = await self.db.fetch_one("SELECT COUNT(*) AS c FROM users")
        return int(row["c"]) if row else 0
