"""AI conversation history + provider usage accounting."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class HistoryRepository(BaseRepository):
    async def add(self, user_id: int, role: str, content: str,
                  provider: str | None = None, model: str | None = None) -> None:
        await self.db.execute(
            "INSERT INTO ai_history (user_id, role, content, provider, model) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, role, content, provider, model),
        )

    async def recent(self, user_id: int, limit: int = 20) -> list[sqlite3.Row]:
        rows = await self.db.fetch_all(
            "SELECT * FROM ai_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        return list(reversed(rows))

    async def clear(self, user_id: int) -> None:
        await self.db.execute("DELETE FROM ai_history WHERE user_id = ?", (user_id,))

    async def record_usage(self, user_id: int | None, provider: str,
                           model: str | None, tokens: int) -> None:
        await self.db.execute(
            "INSERT INTO provider_usage (user_id, provider, model, tokens) VALUES (?, ?, ?, ?)",
            (user_id, provider, model, tokens),
        )
