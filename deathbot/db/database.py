"""Async SQLite access layer built on aiosqlite.

A single long-lived connection is shared across the app (SQLite serialises
writes anyway). Rows come back as ``sqlite3.Row`` so repositories can treat
them like dicts.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

import aiosqlite

from ..logging_setup import get_logger

log = get_logger("db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class Database:
    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._conn: aiosqlite.Connection | None = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database.connect() must be awaited first")
        return self._conn

    async def connect(self) -> None:
        if self._conn is not None:
            return
        # Make sure the directory exists — in a container the DB lives on a
        # mounted volume that may be empty on first start.
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._path)
        self._conn.row_factory = sqlite3.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        log.info("SQLite connected at %s", self._path)

    async def init_schema(self) -> None:
        await self.connect()
        await self._conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        await self._conn.commit()
        log.info("Schema initialised")

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    # ---- thin query helpers -------------------------------------------------
    async def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        cur = await self.conn.execute(sql, params)
        await self.conn.commit()
        lastrowid = cur.lastrowid
        await cur.close()
        return lastrowid or 0

    async def executemany(self, sql: str, seq: Iterable[Sequence[Any]]) -> None:
        await self.conn.executemany(sql, seq)
        await self.conn.commit()

    async def fetch_one(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
        cur = await self.conn.execute(sql, params)
        row = await cur.fetchone()
        await cur.close()
        return row

    async def fetch_all(self, sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
        cur = await self.conn.execute(sql, params)
        rows = await cur.fetchall()
        await cur.close()
        return list(rows)

    async def snapshot(self) -> bytes:
        """Consistent backup of the whole DB (VACUUM INTO a temp file)."""
        import os
        import tempfile

        fd, tmp = tempfile.mkstemp(suffix=".sqlite3", dir="/tmp")
        os.close(fd)
        os.unlink(tmp)  # VACUUM INTO requires the target not to exist
        try:
            await self.conn.execute("VACUUM INTO ?", (tmp,))
            return Path(tmp).read_bytes()
        finally:
            Path(tmp).unlink(missing_ok=True)
