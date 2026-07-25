"""OSINT handlers — whois / dns."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from ..container import Container
from ..util import truncate
from ._guard import guard

router = Router(name="osint")


@router.message(Command("whois"))
async def cmd_whois(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "osint"):
        return
    if not command.args:
        await message.answer("Usage: <code>/whois example.com</code>")
        return
    data = await container.osint.whois(message.from_user.id, command.args.strip())
    await message.answer(f"<b>WHOIS {data['domain']}</b>\n<pre>{truncate(data['raw'], 3000)}</pre>")


@router.message(Command("dns"))
async def cmd_dns(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "osint"):
        return
    if not command.args:
        await message.answer("Usage: <code>/dns example.com</code>")
        return
    data = await container.osint.dns(message.from_user.id, command.args.strip())
    if data["error"]:
        await message.answer(f"❌ {data['error']}")
        return
    addrs = "\n".join(data["addresses"]) or "no records"
    rev = f"\nPTR: {data['reverse']}" if data["reverse"] else ""
    await message.answer(f"<b>DNS {data['host']}</b>\n<pre>{addrs}{rev}</pre>")
