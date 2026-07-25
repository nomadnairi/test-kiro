"""Tiny TTL cache backed by SQLite (used by tool/OSINT lookups)."""
from __future__ import annotations

from .base import BaseRepository


class CacheRepository(BaseRepository):
    async def get(self, key: str) -> str | None:
        row = await self.db.fetch_one(
            "SELECT value FROM cache WHERE key = ? "
            "AND (expires_at IS NULL OR expires_at > datetime('now'))",
            (key,),
        )
        return row["value"] if row else None

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        expires = None
        if ttl_seconds is not None:
            expires = f"+{int(ttl_seconds)} seconds"
        await self.db.execute(
            "INSERT INTO cache (key, value, expires_at) "
            "VALUES (?, ?, CASE WHEN ? IS NULL THEN NULL ELSE datetime('now', ?) END) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, expires_at = excluded.expires_at",
            (key, value, expires, expires),
        )

    async def purge_expired(self) -> int:
        return await self.db.execute(
            "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at <= datetime('now')"
        )
