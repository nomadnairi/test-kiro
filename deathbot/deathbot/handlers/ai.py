"""AI chat handlers — one-shot /ai and a stateful /chat session."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..container import Container
from ..states import AIChat
from ..util import truncate
from ._guard import guard

router = Router(name="ai")


@router.message(Command("providers"))
async def cmd_providers(message: Message, container: Container) -> None:
    if not await guard(message, container, "ai"):
        return
    available = container.ai.available_providers()
    body = ", ".join(available) if available else "none configured (set keys with /addkey)"
    await message.answer(f"<b>AI providers available:</b> {body}")


@router.message(Command("ai"))
async def cmd_ai(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "ai"):
        return
    if not command.args:
        await message.answer("Usage: <code>/ai your question</code>")
        return
    await message.chat.do("typing")
    answer = await container.ai.ask(message.from_user.id, command.args)
    await message.answer(truncate(answer))


@router.message(Command("chat"))
async def cmd_chat_start(message: Message, container: Container, state: FSMContext) -> None:
    if not await guard(message, container, "ai"):
        return
    await state.set_state(AIChat.chatting)
    await message.answer("💬 Chat mode on. Send messages; /stop to exit, /reset to clear history.")


@router.message(Command("stop"), AIChat.chatting)
async def cmd_chat_stop(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("💬 Chat mode off.")


@router.message(Command("reset"))
async def cmd_reset(message: Message, container: Container) -> None:
    if not await guard(message, container, "ai"):
        return
    await container.ai.reset(message.from_user.id)
    await message.answer("🧹 Conversation history cleared.")


@router.message(AIChat.chatting, F.text & ~F.text.startswith("/"))
async def chat_message(message: Message, container: Container) -> None:
    await message.chat.do("typing")
    answer = await container.ai.ask(message.from_user.id, message.text)
    await message.answer(truncate(answer))
