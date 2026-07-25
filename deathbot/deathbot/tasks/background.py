"""Periodic background jobs (cache cleanup, stats). Started alongside the bot."""
from __future__ import annotations

import asyncio

from ..logging_setup import get_logger
from ..repositories import Repositories

log = get_logger("tasks")


class BackgroundTasks:
    def __init__(self, repos: Repositories, interval: int = 300) -> None:
        self.repos = repos
        self.interval = interval
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.interval)
                purged = await self.repos.cache.purge_expired()
                if purged:
                    log.info("cache: purged %d expired entries", purged)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # noqa: BLE001
                log.warning("background loop error: %s", exc)
