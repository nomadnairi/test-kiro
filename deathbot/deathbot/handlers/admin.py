"""Admin handlers — user & access management (admin/owner only)."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from ..container import Container
from ..core.roles import ROLE_ORDER
from ._guard import guard

router = Router(name="admin")


@router.message(Command("users"))
async def cmd_users(message: Message, container: Container) -> None:
    if not await guard(message, container, "admin"):
        return
    users = await container.users.list_users(30)
    lines = [f"<code>{u['id']}</code> @{u['username'] or '—'} — <b>{u['role']}</b>"
             + (" 🚫" if u["is_banned"] else "") for u in users]
    await message.answer("<b>Users</b>\n" + ("\n".join(lines) or "none"))


@router.message(Command("grant"))
async def cmd_grant(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "admin"):
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or parts[1] not in ROLE_ORDER:
        await message.answer(
            "Usage: <code>/grant &lt;user_id&gt; &lt;role&gt;</code>\n"
            f"Roles: {', '.join(ROLE_ORDER)}"
        )
        return
    await container.access.grant(message.from_user.id, int(parts[0]), parts[1])
    await message.answer(f"✅ {parts[0]} is now <b>{parts[1]}</b>.")


@router.message(Command("ban"))
async def cmd_ban(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "admin"):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: <code>/ban &lt;user_id&gt;</code>")
        return
    await container.access.ban(message.from_user.id, int(command.args.strip()), True)
    await message.answer("🚫 Banned.")


@router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "admin"):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: <code>/unban &lt;user_id&gt;</code>")
        return
    await container.access.ban(message.from_user.id, int(command.args.strip()), False)
    await message.answer("✅ Unbanned.")
