"""Start / help / menu."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..container import Container

router = Router(name="start")

HELP = (
    "<b>DeathBot</b> — OSINT / recon / AI assistant\n\n"
    "<b>Core</b>\n"
    "/start /help /menu /profile\n"
    "<b>Productivity</b>\n"
    "/note &lt;text&gt; · /notes · /todo &lt;text&gt; · /todos · /done &lt;id&gt;\n"
    "<b>AI</b>\n"
    "/ai &lt;prompt&gt; · /chat · /reset · /providers\n"
    "<b>OSINT</b>\n"
    "/whois &lt;domain&gt; · /dns &lt;host&gt;\n"
    "<b>Pentest</b> (authorised targets only)\n"
    "/scan &lt;host&gt;\n"
    "<b>Settings</b>\n"
    "/settings · /addkey · /keys\n"
    "<b>Admin</b>\n"
    "/users · /grant · /ban · /audit · /maintenance"
)


@router.message(CommandStart())
async def cmd_start(message: Message, container: Container, role: str = "guest") -> None:
    name = message.from_user.full_name if message.from_user else "there"
    whitelisted = await container.repos.access.is_whitelisted(message.from_user.id)
    status = "✅ active" if whitelisted or role == "owner" else "🔒 awaiting access"
    await message.answer(
        f"👋 Hi {name}!\n"
        f"I'm <b>{container.settings.bot_name}</b>.\n"
        f"Role: <b>{role}</b> · Status: {status}\n\n"
        "Use /help to see what I can do."
    )


@router.message(Command("help", "menu"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP)
