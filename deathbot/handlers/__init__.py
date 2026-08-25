"""Handler layer — a single button-driven menu router (no feature commands)."""
from __future__ import annotations

from aiogram import Router

from . import investigator, menu


def build_root_router() -> Router:
    root = Router(name="root")
    # investigator FIRST: its FSM-guarded handlers must win over menu's
    # catch-all on_stray (@router.message(F.text) matches any text in any
    # state, and aiogram stops at the first matching handler).
    root.include_router(investigator.router)
    root.include_router(menu.router)
    return root


__all__ = ["build_root_router"]
