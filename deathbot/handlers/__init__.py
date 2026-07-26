"""Handler layer — a single button-driven menu router (no feature commands)."""
from __future__ import annotations

from aiogram import Router

from . import menu


def build_root_router() -> Router:
    root = Router(name="root")
    root.include_router(menu.router)
    return root


__all__ = ["build_root_router"]
