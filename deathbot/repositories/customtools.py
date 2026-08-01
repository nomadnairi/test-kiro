"""Persistence for owner-installed runtime tools (see services/plugins.py)."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class CustomToolRepository(BaseRepository):
    async def add(self, tool_id: str, label: str, description: str, spec: str,
                  package_name: str, binary_path: str, created_by: int) -> None:
        await self.db.execute(
            "INSERT INTO custom_tools "
            "(id, label, description, spec, package_name, binary_path, created_by) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tool_id, label, description, spec, package_name, binary_path, created_by),
        )

    async def list_all(self) -> list[sqlite3.Row]:
        return await self.db.fetch_all("SELECT * FROM custom_tools ORDER BY created_at DESC")

    async def get(self, tool_id: str) -> sqlite3.Row | None:
        return await self.db.fetch_one("SELECT * FROM custom_tools WHERE id = ?", (tool_id,))

    async def delete(self, tool_id: str) -> bool:
        row = await self.get(tool_id)
        if row is None:
            return False
        await self.db.execute("DELETE FROM custom_tools WHERE id = ?", (tool_id,))
        return True
