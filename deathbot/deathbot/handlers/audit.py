"""Audit log viewer (admin/owner)."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..container import Container
from ._guard import guard

router = Router(name="audit")


@router.message(Command("audit"))
async def cmd_audit(message: Message, container: Container) -> None:
    if not await guard(message, container, "audit"):
        return
    rows = await container.repos.audit.recent(25)
    if not rows:
        await message.answer("No audit entries yet.")
        return
    lines = [f"{r['created_at']} · <code>{r['user_id']}</code> · {r['action']} {r['detail'] or ''}"
             for r in rows]
    await message.answer("<b>Recent audit log</b>\n" + "\n".join(lines))
