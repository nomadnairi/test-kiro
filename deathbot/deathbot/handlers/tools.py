"""Tooling introspection — which external binaries / export formats are usable."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..container import Container
from ..util import has_binary
from ._guard import guard

router = Router(name="tools")

_EXTERNAL = ["nmap", "whois", "masscan", "amass", "subfinder", "nuclei", "httpx", "dig"]


@router.message(Command("tools"))
async def cmd_tools(message: Message, container: Container) -> None:
    if not await guard(message, container, "tools"):
        return
    lines = [f"{'✅' if has_binary(t) else '➖'} {t}" for t in _EXTERNAL]
    exports = ", ".join(container.export.available_formats())
    await message.answer(
        "<b>External tools</b>\n" + "\n".join(lines) +
        f"\n\n<b>Export formats:</b> {exports}"
    )
