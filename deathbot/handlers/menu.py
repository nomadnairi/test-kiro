"""The entire button UI: menu navigation + a registry-driven tool runner.

There are no feature commands — every capability is reached by tapping buttons.
Only /start, /menu and /cancel exist to bootstrap or reset the interface.
"""
from __future__ import annotations

import io

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from datetime import datetime, timezone

from ..container import Container
from ..keyboards import cancel_menu, category_menu, export_menu, main_menu, result_menu
from ..registry import Result, Tool, build_export, get_tool, save_last_report, strip_html
from ..states import AIChat, ApiKeyFlow, ToolFlow
from ..util import truncate

router = Router(name="menu")

_REASONS = {
    "banned": "🚫 Ты забанен.",
    "not_whitelisted": "🔒 Доступ закрыт — тебя нет в списке. Попроси доступ у владельца.",
    "module_disabled": "⛔ Этот раздел отключён.",
    "insufficient_role": "⛔ Твоя роль не позволяет это.",
}
_WELCOME = (
    "💀 <b>DeathBot</b>\n"
    "Всё управляется кнопками ниже — просто нажимай.\n"
    "OSINT · Пентест · ИИ · Агенты · Заметки · Экспорт"
)


def _visible(container: Container, role: str):
    """Sync predicate for menu building (role matrix + owner)."""
    return lambda module: container.access.role_can_use(role, module)


async def _deny_reason(container: Container, uid: int, module: str) -> str | None:
    decision = await container.access.check(uid, module)
    return None if decision.allowed else _REASONS.get(decision.reason, "⛔ Доступ закрыт.")


# --------------------------------------------------------------------------- #
# entry commands (the only commands that exist)
# --------------------------------------------------------------------------- #
@router.message(CommandStart())
@router.message(Command("menu"))
async def cmd_menu(message: Message, container: Container, state: FSMContext,
                   role: str = "guest") -> None:
    await state.clear()
    await message.answer(_WELCOME, reply_markup=main_menu(_visible(container, role)))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, container: Container, state: FSMContext,
                     role: str = "guest") -> None:
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu(_visible(container, role)))


# --------------------------------------------------------------------------- #
# navigation callbacks
# --------------------------------------------------------------------------- #
@router.callback_query(F.data == "nav:main")
async def cb_main(cb: CallbackQuery, container: Container, state: FSMContext,
                  role: str = "guest") -> None:
    await state.clear()
    await cb.message.edit_text(_WELCOME, reply_markup=main_menu(_visible(container, role)))
    await cb.answer()


@router.callback_query(F.data == "nav:cancel")
async def cb_cancel(cb: CallbackQuery, container: Container, state: FSMContext,
                    role: str = "guest") -> None:
    await state.clear()
    await cb.message.edit_text(_WELCOME, reply_markup=main_menu(_visible(container, role)))
    await cb.answer("Отменено")


@router.callback_query(F.data == "exp:pick")
async def cb_export_pick(cb: CallbackQuery, container: Container) -> None:
    formats = container.export.available_formats()
    await cb.message.answer(
        "📤 <b>Сохранить последний результат</b>\nВыбери формат:",
        reply_markup=export_menu(formats, container.export.LABELS),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("exp:fmt:"))
async def cb_export_fmt(cb: CallbackQuery, container: Container) -> None:
    fmt = cb.data.split(":", 2)[2]
    await cb.answer("Готовлю файл…")
    try:
        result = await build_export(container, cb.from_user.id, fmt)
    except Exception as exc:  # noqa: BLE001
        await cb.message.answer(f"⚠️ Не удалось экспортировать: {exc}")
        return
    await cb.message.answer_document(
        BufferedInputFile(result.file_bytes, filename=result.filename),
        caption=result.text,
    )


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cb: CallbackQuery, container: Container, state: FSMContext,
                      role: str = "guest") -> None:
    await state.clear()
    category = cb.data.split(":", 1)[1]
    from ..registry import CATEGORIES
    label = dict(CATEGORIES).get(category, category)
    await cb.message.edit_text(
        f"{label}\nВыбери инструмент:",
        reply_markup=category_menu(category, _visible(container, role)),
    )
    await cb.answer()


# --------------------------------------------------------------------------- #
# tool tap
# --------------------------------------------------------------------------- #
@router.callback_query(F.data.startswith("tool:"))
async def cb_tool(cb: CallbackQuery, container: Container, state: FSMContext) -> None:
    tool = get_tool(cb.data.split(":", 1)[1])
    if tool is None:
        await cb.answer("Неизвестный инструмент", show_alert=True)
        return

    reason = await _deny_reason(container, cb.from_user.id, tool.module)
    if reason:
        await cb.answer(reason, show_alert=True)
        return

    if tool.kind == "instant":
        await cb.answer("Выполняю…")
        await _run_and_reply(cb.message, container, cb.from_user.id, tool, "")
        return

    if tool.kind == "chat":
        await state.set_state(AIChat.chatting)
        await cb.message.edit_text(
            "💬 <b>Режим диалога</b> — пиши сообщения. Нажми «Отмена», чтобы выйти.",
            reply_markup=cancel_menu(),
        )
        await cb.answer()
        return

    if tool.kind == "apikey":
        await state.set_state(ApiKeyFlow.waiting_provider)
        await cb.message.edit_text(
            "Какой провайдер? (openrouter, openai, claude, gemini, shodan, hibp…)",
            reply_markup=cancel_menu(),
        )
        await cb.answer()
        return

    # input / photo → stash the tool and prompt
    await state.set_state(ToolFlow.waiting_photo if tool.kind == "photo" else ToolFlow.waiting_input)
    await state.update_data(tool_id=tool.id, category=tool.category)
    await cb.message.edit_text(f"<b>{tool.label}</b>\n{tool.prompt}", reply_markup=cancel_menu())
    await cb.answer()


# --------------------------------------------------------------------------- #
# input dispatch
# --------------------------------------------------------------------------- #
@router.message(ToolFlow.waiting_input, F.text & ~F.text.startswith("/"))
async def on_input(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    tool = get_tool(data.get("tool_id", ""))
    await state.clear()
    if tool is None or tool.run is None:
        await message.answer("Сессия истекла — открой /menu заново.")
        return
    await message.chat.do("typing")
    await _run_and_reply(message, container, message.from_user.id, tool, message.text)


@router.message(ToolFlow.waiting_photo, F.photo | F.document)
async def on_photo(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category", "osint")
    await state.clear()
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    buf = io.BytesIO()
    await message.bot.download(file_id, destination=buf)
    result = container.osint.exif(buf.getvalue())
    from ..registry import human
    text = human("Метаданные / EXIF", result)
    await save_last_report(container, message.from_user.id, {
        "title": "Metadata / EXIF",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tags": ["deathbot", "osint", "exif"],
        "sections": {"EXIF": strip_html(text)},
    })
    await message.answer(text, reply_markup=result_menu(category, exportable=True))


@router.message(AIChat.chatting, F.text & ~F.text.startswith("/"))
async def on_chat(message: Message, container: Container) -> None:
    await message.chat.do("typing")
    answer = await container.ai.ask(message.from_user.id, message.text)
    await message.answer(truncate(answer), reply_markup=cancel_menu())


# ---- API-key two-step flow ----
@router.message(ApiKeyFlow.waiting_provider, F.text & ~F.text.startswith("/"))
async def on_key_provider(message: Message, state: FSMContext) -> None:
    await state.update_data(provider=message.text.strip().lower())
    await state.set_state(ApiKeyFlow.waiting_value)
    await message.answer("Теперь отправь API-ключ. Он будет зашифрован (AES-256-GCM).",
                         reply_markup=cancel_menu())


@router.message(ApiKeyFlow.waiting_value, F.text & ~F.text.startswith("/"))
async def on_key_value(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    provider = data.get("provider", "unknown")
    await container.api_keys.set_key(message.from_user.id, provider, message.text.strip())
    await state.clear()
    try:
        await message.delete()  # scrub the plaintext key from the chat
    except Exception:  # noqa: BLE001
        pass
    await message.answer(f"🔐 Ключ для {provider} сохранён (зашифрован).",
                         reply_markup=result_menu("settings"))


# ---- fallback: any stray text opens the menu ----
@router.message(F.text)
async def on_stray(message: Message, container: Container, role: str = "guest") -> None:
    await message.answer(_WELCOME, reply_markup=main_menu(_visible(container, role)))


# --------------------------------------------------------------------------- #
# shared runner
# --------------------------------------------------------------------------- #
async def _run_and_reply(message: Message, container: Container, uid: int,
                         tool: Tool, arg: str) -> None:
    try:
        result: Result = await tool.run(container, uid, arg)
    except Exception as exc:  # noqa: BLE001 — surface tool errors to the user
        await message.answer(f"⚠️ Ошибка «{tool.label}»: {exc}",
                             reply_markup=result_menu(tool.category))
        return

    if result.file_bytes is not None and result.filename:
        await message.answer_document(
            BufferedInputFile(result.file_bytes, filename=result.filename),
            caption=result.text or None,
        )
        await message.answer("Готово.", reply_markup=result_menu(tool.category))
    else:
        # Remember this result so the user can re-export it in any format.
        await save_last_report(container, uid, {
            "title": f"{tool.label}{f': {arg}' if arg else ''}",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tags": ["deathbot", tool.category],
            "sections": {tool.label: strip_html(result.text)},
        })
        await message.answer(truncate(result.text),
                             reply_markup=result_menu(tool.category, exportable=True))
