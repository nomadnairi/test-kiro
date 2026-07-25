"""Tool Execution Engine — an async task queue with bounded worker concurrency,
per-task timeout and retry. Long-running OSINT/pentest jobs are submitted here
instead of blocking a handler.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

from ..logging_setup import get_logger

log = get_logger("tools.engine")

Job = Callable[[], Awaitable[Any]]


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    job: Job
    timeout: int = 120
    retries: int = 1
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    _future: asyncio.Future = field(default_factory=asyncio.Future, repr=False)


class TaskEngine:
    def __init__(self, workers: int = 4) -> None:
        self._queue: asyncio.Queue[Task] = asyncio.Queue()
        self._tasks: dict[str, Task] = {}
        self._workers = workers
        self._running: list[asyncio.Task] = []

    async def start(self) -> None:
        if self._running:
            return
        self._running = [
            asyncio.create_task(self._worker(i)) for i in range(self._workers)
        ]
        log.info("Task engine started with %d workers", self._workers)

    async def stop(self) -> None:
        for w in self._running:
            w.cancel()
        self._running.clear()

    def submit(self, job: Job, *, timeout: int = 120, retries: int = 1) -> Task:
        task = Task(id=uuid.uuid4().hex[:12], job=job, timeout=timeout, retries=retries)
        self._tasks[task.id] = task
        self._queue.put_nowait(task)
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    async def _worker(self, index: int) -> None:
        while True:
            task = await self._queue.get()
            task.status = TaskStatus.RUNNING
            attempt = 0
            while attempt < max(1, task.retries):
                attempt += 1
                try:
                    task.result = await asyncio.wait_for(task.job(), timeout=task.timeout)
                    task.status = TaskStatus.DONE
                    break
                except Exception as exc:  # noqa: BLE001 — surface via task state
                    task.error = f"{type(exc).__name__}: {exc}"
                    task.status = TaskStatus.FAILED
                    log.warning("task %s attempt %d failed: %s", task.id, attempt, task.error)
            if not task._future.done():
                task._future.set_result(task)
            self._queue.task_done()

    async def wait(self, task: Task) -> Task:
        return await task._future
