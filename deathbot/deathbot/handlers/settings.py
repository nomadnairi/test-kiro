"""Settings + encrypted API-key management (FSM)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..container import Container
from ..states import ApiKeyFlow
from ._guard import guard

router = Router(name="settings")


@router.message(Command("settings"))
async def cmd_settings(message: Message, container: Container) -> None:
    if not await guard(message, container, "profile"):
        return
    s = await container.settings_svc.all(message.from_user.id)
    await message.answer(
        "<b>Settings</b>\n"
        f"AI provider: {s['ai_provider'] or 'auto'}\n"
        f"AI model: {s['ai_model'] or 'default'}\n"
        f"Language: {s['language']}\n\n"
        "Change with <code>/setprovider openrouter</code> or add keys via /addkey."
    )


@router.message(Command("setprovider"))
async def cmd_setprovider(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "profile"):
        return
    if not command.args:
        await message.answer("Usage: <code>/setprovider openrouter</code>")
        return
    await container.settings_svc.set(message.from_user.id, "ai_provider", command.args.strip())
    await message.answer(f"✅ AI provider set to {command.args.strip()}")


@router.message(Command("keys"))
async def cmd_keys(message: Message, container: Container) -> None:
    if not await guard(message, container, "profile"):
        return
    providers = await container.api_keys.list_providers(message.from_user.id)
    await message.answer("🔑 Stored keys: " + (", ".join(providers) or "none"))


@router.message(Command("addkey"))
async def cmd_addkey(message: Message, container: Container, state: FSMContext) -> None:
    if not await guard(message, container, "profile"):
        return
    await state.set_state(ApiKeyFlow.waiting_provider)
    await message.answer("Which provider? (e.g. openrouter, openai, groq). /cancel to abort.")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is not None:
        await state.clear()
        await message.answer("Cancelled.")


@router.message(ApiKeyFlow.waiting_provider, F.text)
async def addkey_provider(message: Message, state: FSMContext) -> None:
    await state.update_data(provider=message.text.strip().lower())
    await state.set_state(ApiKeyFlow.waiting_value)
    await message.answer("Now send the API key. It will be encrypted (AES-256-GCM) at rest.")


@router.message(ApiKeyFlow.waiting_value, F.text)
async def addkey_value(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    provider = data.get("provider", "unknown")
    await container.api_keys.set_key(message.from_user.id, provider, message.text.strip())
    await state.clear()
    try:
        await message.delete()  # remove the plaintext key from the chat
    except Exception:  # noqa: BLE001
        pass
    await message.answer(f"🔐 Stored encrypted key for {provider}.")
