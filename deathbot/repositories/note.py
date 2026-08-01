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

    async def update(self, note_id: int, user_id: int, title: str, body: str) -> bool:
        before = await self.get(note_id, user_id)
        if before is None:
            return False
        await self.db.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = datetime('now') "
            "WHERE id = ? AND user_id = ?",
            (title, body, note_id, user_id),
        )
        return True

    async def search(self, user_id: int, query: str, limit: int = 20) -> list[sqlite3.Row]:
        like = f"%{query}%"
        return await self.db.fetch_all(
            "SELECT * FROM notes WHERE user_id = ? AND (title LIKE ? OR body LIKE ?) "
            "ORDER BY updated_at DESC LIMIT ?",
            (user_id, like, like, limit),
        )

    async def count(self, user_id: int) -> int:
        row = await self.db.fetch_one(
            "SELECT COUNT(*) AS n FROM notes WHERE user_id = ?", (user_id,))
        return row["n"] if row else 0

    async def delete_all(self, user_id: int) -> int:
        n = await self.count(user_id)
        if n:
            await self.db.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        return n
