"""Encrypted per-user API keys (ciphertext only lives here)."""
from __future__ import annotations

import sqlite3

from .base import BaseRepository


class ApiKeyRepository(BaseRepository):
    async def set(self, user_id: int, provider: str, ciphertext: str) -> None:
        await self.db.execute(
            "INSERT INTO api_keys (user_id, provider, ciphertext) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, provider) DO UPDATE SET ciphertext = excluded.ciphertext",
            (user_id, provider, ciphertext),
        )

    async def get(self, user_id: int, provider: str) -> str | None:
        row = await self.db.fetch_one(
            "SELECT ciphertext FROM api_keys WHERE user_id = ? AND provider = ?",
            (user_id, provider),
        )
        return row["ciphertext"] if row else None

    async def list_providers(self, user_id: int) -> list[str]:
        rows = await self.db.fetch_all(
            "SELECT provider FROM api_keys WHERE user_id = ?", (user_id,)
        )
        return [r["provider"] for r in rows]

    async def delete(self, user_id: int, provider: str) -> None:
        await self.db.execute(
            "DELETE FROM api_keys WHERE user_id = ? AND provider = ?", (user_id, provider)
        )

    async def delete_all(self, user_id: int) -> None:
        await self.db.execute("DELETE FROM api_keys WHERE user_id = ?", (user_id,))
