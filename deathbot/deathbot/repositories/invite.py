"""Invite codes."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class InviteRepository(BaseRepository):
    async def create(self, code: str, role: str, created_by: int,
                     expires_at: str | None = None) -> None:
        await self.db.execute(
            "INSERT INTO invites (code, role, created_by, expires_at) VALUES (?, ?, ?, ?)",
            (code, role, created_by, expires_at),
        )

    async def get(self, code: str) -> sqlite3.Row | None:
        return await self.db.fetch_one("SELECT * FROM invites WHERE code = ?", (code,))

    async def mark_used(self, code: str, used_by: int) -> None:
        await self.db.execute(
            "UPDATE invites SET used_by = ?, used_at = datetime('now') WHERE code = ?",
            (used_by, code),
        )

    async def list_open(self) -> list[sqlite3.Row]:
        return await self.db.fetch_all("SELECT * FROM invites WHERE used_by IS NULL")
