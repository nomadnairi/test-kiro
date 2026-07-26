"""Notes persistence."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class NoteRepository(BaseRepository):
    async def add(self, user_id: int, title: str, body: str) -> int:
        return await self.db.execute(
            "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body),
        )

    async def get(self, note_id: int, user_id: int) -> sqlite3.Row | None:
        return await self.db.fetch_one(
            "SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)
        )

    async def list(self, user_id: int, limit: int = 50) -> list[sqlite3.Row]:
        return await self.db.fetch_all(
            "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?",
            (user_id, limit),
        )

    async def delete(self, note_id: int, user_id: int) -> bool:
        before = await self.get(note_id, user_id)
        if before is None:
            return False
        await self.db.execute(
            "DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)
        )
        return True
