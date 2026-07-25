"""Audit trail."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class AuditRepository(BaseRepository):
    async def log(self, user_id: int | None, action: str, detail: str = "") -> None:
        await self.db.execute(
            "INSERT INTO audit_logs (user_id, action, detail) VALUES (?, ?, ?)",
            (user_id, action, detail),
        )

    async def recent(self, limit: int = 50, user_id: int | None = None) -> list[sqlite3.Row]:
        if user_id is not None:
            return await self.db.fetch_all(
                "SELECT * FROM audit_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            )
        return await self.db.fetch_all(
            "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)
        )
