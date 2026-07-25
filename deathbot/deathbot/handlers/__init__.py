"""Handler layer — aggregates every feature router into one."""
from __future__ import annotations

from aiogram import Router

from . import (
    admin,
    ai,
    audit,
    notes,
    osint,
    pentest,
    profile,
    settings,
    start,
    stubs,
    todo,
    tools,
)


def build_root_router() -> Router:
    root = Router(name="root")
    root.include_routers(
        start.router,
        profile.router,
        settings.router,
        notes.router,
        todo.router,
        ai.router,
        osint.router,
        pentest.router,
        tools.router,
        admin.router,
        audit.router,
        stubs.router,
    )
    return root


__all__ = ["build_root_router"]
