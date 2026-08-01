"""Todo persistence."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class TodoRepository(BaseRepository):
    async def add(self, user_id: int, text: str) -> int:
        return await self.db.execute(
            "INSERT INTO todos (user_id, text) VALUES (?, ?)", (user_id, text)
        )

    async def list(self, user_id: int, include_done: bool = True) -> list[sqlite3.Row]:
        sql = "SELECT * FROM todos WHERE user_id = ?"
        if not include_done:
            sql += " AND done = 0"
        sql += " ORDER BY done ASC, created_at DESC"
        return await self.db.fetch_all(sql, (user_id,))

    async def set_done(self, todo_id: int, user_id: int, done: bool = True) -> bool:
        row = await self.db.fetch_one(
            "SELECT id FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id)
        )
        if row is None:
            return False
        await self.db.execute(
            "UPDATE todos SET done = ?, completed_at = CASE WHEN ? THEN datetime('now') END "
            "WHERE id = ? AND user_id = ?",
            (1 if done else 0, 1 if done else 0, todo_id, user_id),
        )
        return True

    async def delete(self, todo_id: int, user_id: int) -> bool:
        row = await self.db.fetch_one(
            "SELECT id FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id)
        )
        if row is None:
            return False
        await self.db.execute(
            "DELETE FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id)
        )
        return True

    async def update_text(self, todo_id: int, user_id: int, text: str) -> bool:
        row = await self.db.fetch_one(
            "SELECT id FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id)
        )
        if row is None:
            return False
        await self.db.execute(
            "UPDATE todos SET text = ? WHERE id = ? AND user_id = ?", (text, todo_id, user_id)
        )
        return True

    async def clear_done(self, user_id: int) -> int:
        done_rows = await self.db.fetch_all(
            "SELECT id FROM todos WHERE user_id = ? AND done = 1", (user_id,))
        if done_rows:
            await self.db.execute("DELETE FROM todos WHERE user_id = ? AND done = 1", (user_id,))
        return len(done_rows)

    async def delete_all(self, user_id: int) -> int:
        pending, done = await self.counts(user_id)
        total = pending + done
        if total:
            await self.db.execute("DELETE FROM todos WHERE user_id = ?", (user_id,))
        return total

    async def counts(self, user_id: int) -> tuple[int, int]:
        """(pending, done)."""
        row = await self.db.fetch_one(
            "SELECT SUM(done = 0) AS pending, SUM(done = 1) AS done "
            "FROM todos WHERE user_id = ?", (user_id,))
        return (row["pending"] or 0, row["done"] or 0) if row else (0, 0)
