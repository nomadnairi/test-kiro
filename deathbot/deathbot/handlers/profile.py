"""Profile."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..container import Container
from ._guard import guard

router = Router(name="profile")


@router.message(Command("profile", "me"))
async def cmd_profile(message: Message, container: Container) -> None:
    if not await guard(message, container, "profile"):
        return
    p = await container.users.profile(message.from_user.id)
    if not p:
        await message.answer("No profile yet — send /start first.")
        return
    providers = ", ".join(p["providers"]) or "—"
    await message.answer(
        "<b>Your profile</b>\n"
        f"ID: <code>{p['id']}</code>\n"
        f"Username: @{p['username'] or '—'}\n"
        f"Role: <b>{p['role']}</b>\n"
        f"Notes: {p['notes']} · Todos: {p['todos']}\n"
        f"AI keys: {providers}\n"
        f"Since: {p['created_at']}"
    )
